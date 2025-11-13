"""
AI-Powered File Categorizer - Uses LLM to intelligently categorize files
Supports both OpenAI and free Hugging Face models
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from file_scanner import FileInfo

load_dotenv()


class FileCategorizer:
    """Uses LLM to categorize files intelligently"""
    
    # Default categories
    DEFAULT_CATEGORIES = [
        "Documents", "Images", "Videos", "Audio", "Archives",
        "Code", "Projects", "Downloads", "Desktop", "Spreadsheets",
        "Presentations", "PDFs", "Installers", "Fonts", "Other"
    ]
    
    def __init__(
        self,
        provider: str = "auto",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize categorizer
        
        Args:
            provider: "openai", "huggingface", or "auto" (auto-detect)
            api_key: API key for the provider (optional, can use env vars)
            model_name: Specific model to use (optional)
        """
        self.provider = provider
        self.model_name = model_name
        self.client = None
        self.hf_model = None
        self.hf_tokenizer = None
        
        # Auto-detect provider
        if provider == "auto":
            self.provider = self._detect_provider()
        
        # Initialize based on provider
        if self.provider == "openai":
            self._init_openai(api_key)
        elif self.provider == "huggingface":
            self._init_huggingface(model_name)
        else:
            # Fallback to rule-based only
            print("Warning: No LLM provider configured. Using rule-based categorization only.")
            self.provider = "rule-based"
        
        self.preferences: Dict = {}
        self._load_preferences()
    
    def _detect_provider(self) -> str:
        """Auto-detect which provider to use based on available credentials"""
        # Check for OpenAI key
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        # Check for Hugging Face token (optional for inference API)
        elif os.getenv("HUGGINGFACE_API_TOKEN"):
            return "huggingface"
        # Try to use local Hugging Face model
        else:
            try:
                import transformers
                return "huggingface"
            except ImportError:
                return "rule-based"
    
    def _init_openai(self, api_key: Optional[str] = None):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env file")
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def _init_huggingface(self, model_name: Optional[str] = None):
        """Initialize Hugging Face model (local or API)"""
        # Default to a small, efficient model
        # Options: microsoft/Phi-3-mini-4k-instruct, Qwen/Qwen2.5-0.5B-Instruct, etc.
        self.model_name = model_name or os.getenv(
            "HUGGINGFACE_MODEL",
            "microsoft/Phi-3-mini-4k-instruct"  # Small, efficient, free
        )
        
        # Check if using Inference API or local model
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        
        if hf_token:
            # Use Inference API (free tier available)
            self.use_inference_api = True
            self.hf_token = hf_token
            print(f"Using Hugging Face Inference API with model: {self.model_name}")
        else:
            # Use local model
            self.use_inference_api = False
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch
                
                print(f"Loading Hugging Face model: {self.model_name}")
                print("(This may take a moment on first run as the model downloads...)")
                
                self.hf_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                # Set pad token if not set
                if self.hf_tokenizer.pad_token is None:
                    self.hf_tokenizer.pad_token = self.hf_tokenizer.eos_token
                
                # Load model with appropriate settings
                # Check for Apple Silicon (MPS) or CUDA
                use_mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
                use_cuda = torch.cuda.is_available()
                
                model_kwargs = {}
                
                if use_cuda:
                    # NVIDIA GPU
                    model_kwargs["torch_dtype"] = torch.float16
                    model_kwargs["device_map"] = "auto"
                elif use_mps:
                    # Apple Silicon (M1/M2/M3)
                    model_kwargs["torch_dtype"] = torch.float16
                    # MPS device will be set after loading
                else:
                    # CPU only
                    model_kwargs["torch_dtype"] = torch.float32
                
                self.hf_model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    **model_kwargs
                )
                
                # Move to appropriate device
                if use_cuda:
                    # Already on GPU via device_map
                    pass
                elif use_mps:
                    self.hf_model = self.hf_model.to("mps")
                    print("Using Apple Silicon (Metal) acceleration")
                else:
                    self.hf_model = self.hf_model.to("cpu")
                
                print("Model loaded successfully!")
            except ImportError:
                print("Warning: transformers not installed. Install with: pip install transformers torch")
                print("Falling back to rule-based categorization...")
                self.provider = "rule-based"
            except Exception as e:
                print(f"Error loading local model: {e}")
                print("Falling back to rule-based categorization...")
                self.provider = "rule-based"
    
    def _load_preferences(self):
        """Load user preferences from file"""
        prefs_file = Path("preferences.json")
        if prefs_file.exists():
            try:
                with open(prefs_file, 'r') as f:
                    self.preferences = json.load(f)
            except:
                self.preferences = {}
        else:
            self.preferences = {}
    
    def _save_preferences(self):
        """Save user preferences to file"""
        prefs_file = Path("preferences.json")
        with open(prefs_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def categorize_files(self, files: List[FileInfo], batch_size: int = 20) -> Dict[FileInfo, Dict]:
        """Categorize a list of files using LLM"""
        results = {}
        
        # Process in batches to avoid token limits
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            batch_results = self._categorize_batch(batch)
            results.update(batch_results)
        
        return results
    
    def _categorize_batch(self, files: List[FileInfo]) -> Dict[FileInfo, Dict]:
        """Categorize a batch of files"""
        # Prepare file information for LLM
        file_descriptions = []
        for file in files:
            desc = {
                "name": file.name,
                "extension": file.extension,
                "mime_type": file.mime_type,
                "size_mb": round(file.size / (1024 * 1024), 2),
                "modified": file.modified.strftime("%Y-%m-%d")
            }
            file_descriptions.append(desc)
        
        # Build prompt with preferences
        preferences_text = ""
        if self.preferences.get("category_rules"):
            preferences_text = f"\n\nUser preferences:\n{json.dumps(self.preferences['category_rules'], indent=2)}"
        
        prompt = f"""You are a file organization assistant. Categorize the following files into appropriate categories.

Available categories: {', '.join(self.DEFAULT_CATEGORIES)}

For each file, provide:
1. category: The main category (from the list above)
2. subcategory: A more specific subcategory if applicable (e.g., "Photos", "Screenshots" for Images)
3. project: If the file belongs to a specific project, identify it
4. suggested_name: A cleaner, more descriptive name if the current name is unclear
5. confidence: Your confidence level (0.0 to 1.0)
6. reason: Brief explanation of your categorization

Files to categorize:
{json.dumps(file_descriptions, indent=2)}
{preferences_text}

Return a JSON object where keys are file names and values are categorization objects with the fields above.
"""
        
        try:
            if self.provider == "openai":
                result = self._categorize_with_openai(prompt)
            elif self.provider == "huggingface":
                result = self._categorize_with_huggingface(prompt)
            else:
                # Rule-based fallback
                return {file: self._fallback_categorize(file) for file in files}
            
            # Map results back to FileInfo objects
            categorized = {}
            for file in files:
                if file.name in result:
                    categorized[file] = result[file.name]
                else:
                    # Fallback categorization
                    categorized[file] = self._fallback_categorize(file)
            
            return categorized
            
        except Exception as e:
            print(f"Error in LLM categorization: {e}")
            # Fallback to rule-based categorization
            return {file: self._fallback_categorize(file) for file in files}
    
    def _categorize_with_openai(self, prompt: str) -> Dict:
        """Categorize using OpenAI API"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful file organization assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    def _categorize_with_huggingface(self, prompt: str) -> Dict:
        """Categorize using Hugging Face (local or Inference API)"""
        if self.use_inference_api:
            return self._categorize_with_hf_api(prompt)
        else:
            return self._categorize_with_hf_local(prompt)
    
    def _categorize_with_hf_api(self, prompt: str) -> Dict:
        """Categorize using Hugging Face Inference API (free tier)"""
        import requests
        import time
        
        api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        # Format prompt - try different formats for different models
        # For chat models, use chat format; for base models, use simple format
        if "instruct" in self.model_name.lower() or "chat" in self.model_name.lower():
            formatted_prompt = f"""<|system|>
You are a helpful file organization assistant. Always respond with valid JSON only.<|end|>
<|user|>
{prompt}

Respond with only valid JSON, no other text.<|end|>
<|assistant|>
"""
        else:
            # For base models, use simpler format
            formatted_prompt = f"""Task: Categorize files into organized categories.

{prompt}

Respond with only valid JSON:
"""
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 2000,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            # Handle model loading (first request)
            if response.status_code == 503:
                print("Model is loading, waiting 10 seconds...")
                time.sleep(10)
                response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                result_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                result_text = result.get("generated_text", str(result))
            else:
                result_text = str(result)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Try parsing the whole thing
                return json.loads(result_text)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse JSON from model response: {result_text[:200]}")
    
    def _categorize_with_hf_local(self, prompt: str) -> Dict:
        """Categorize using local Hugging Face model"""
        if not self.hf_model or not self.hf_tokenizer:
            raise ValueError("Hugging Face model not initialized")
        
        import torch
        
        # Format prompt
        formatted_prompt = f"""<|system|>
You are a helpful file organization assistant. Always respond with valid JSON only.<|end|>
<|user|>
{prompt}

Respond with only valid JSON, no other text.<|end|>
<|assistant|>
"""
        
        # Tokenize
        inputs = self.hf_tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )
        
        # Move to device if using GPU or Apple Silicon
        device = next(self.hf_model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.hf_model.generate(
                **inputs,
                max_new_tokens=2000,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.hf_tokenizer.eos_token_id
            )
        
        # Decode
        result_text = self.hf_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError(f"Could not parse JSON from model response")
    
    def _fallback_categorize(self, file: FileInfo) -> Dict:
        """Fallback categorization based on file extension and MIME type"""
        ext = file.extension.lower()
        mime = file.mime_type or ""
        
        # Document types
        if ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']:
            category = "Documents"
        # Images
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'] or 'image' in mime:
            category = "Images"
        # Videos
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'] or 'video' in mime:
            category = "Videos"
        # Audio
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg'] or 'audio' in mime:
            category = "Audio"
        # Archives
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            category = "Archives"
        # Code
        elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.json', '.xml']:
            category = "Code"
        # Spreadsheets
        elif ext in ['.xls', '.xlsx', '.csv', '.ods']:
            category = "Spreadsheets"
        # Presentations
        elif ext in ['.ppt', '.pptx', '.odp']:
            category = "Presentations"
        # Installers
        elif ext in ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm']:
            category = "Installers"
        else:
            category = "Other"
        
        return {
            "category": category,
            "subcategory": None,
            "project": None,
            "suggested_name": file.name,
            "confidence": 0.7,
            "reason": f"Categorized by extension: {ext}"
        }
    
    def learn_from_feedback(self, file_name: str, correct_category: str, feedback: str):
        """Learn from user feedback to improve categorization"""
        if "category_rules" not in self.preferences:
            self.preferences["category_rules"] = {}
        
        if "feedback_history" not in self.preferences:
            self.preferences["feedback_history"] = []
        
        # Store feedback
        self.preferences["feedback_history"].append({
            "file": file_name,
            "correct_category": correct_category,
            "feedback": feedback,
            "timestamp": str(Path(file_name).stat().st_mtime)
        })
        
        # Update rules based on feedback
        if correct_category not in self.preferences["category_rules"]:
            self.preferences["category_rules"][correct_category] = []
        
        # Extract patterns from feedback
        self.preferences["category_rules"][correct_category].append({
            "file": file_name,
            "pattern": feedback
        })
        
        self._save_preferences()

