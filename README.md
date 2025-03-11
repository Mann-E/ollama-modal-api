# Ollama as API on Modal

## Serving 

```
modal serve ollama-modal.py
```

## Deployment

```
modal deploy ollama-modal.py
```

## API Interaction 

When you `serve` or `deploy` your Ollama instance to modal, you will get a link like `https://your-org-name--your-app-name-main-dev.modal.run`. This name will be appeared to you just after running one of the above commands and you can use it in curl, python code, etc. 

## Tested models (Ollama Repository IDs) and GPU's

- `gemma2:9b` : `a10g` (Default tests)
- `gemma2:27b` : `a100`
- `haghiri/hormoz:iq4_nl` : `a100`, `h100` (and due to the size, it is fine on `a10g` as well.)
- `mistral-small` : `h100`
- `mistral-large` : `h100:4` (gets too expensive)
- `SIGJNF/deepseek-r1-671b-1.58bit` : `h100:4` (gets too expensive)
- `haghiri/jabir-400b:q4_k` : `h100:4` (gets too expensive)