# Ollama as API on Modal

<p align="center">
    <img src="./llama.jpg" width="512px" height="512px" />
</p>

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

### Request structure 

The request is a simple JSON object like the following:

```json
{
    "messages" : [
        {
            "role" : "user",
            "content" : "What is the answer to universe, life and everything?"
        }
    ]
}
```

Remember that this API is _NOT_ OpenAI compatible, but since the result and request body is identical to OpenAI's, you may be able to make it a part of an OpenAI compatible API. 

### Sample request

```bash
curl --location --request POST 'https://your-org-name--your-app-name-main-dev.modal.run' \
--header 'Content-Type: application/json' \
--data-raw '{
    "messages" : [
        {
            "role" : "user",
            "content" : "write a joke on Elon Musk"
        }
    ]
}'
```

## Tested models (Ollama Repository IDs) and GPU's

- `qwen3:14b` : `a100` (May work fine on smaller GPU as well.)
- `gemma2:9b` : `a10g` (Default tests)
- `gemma2:27b` : `a100`
- `haghiri/hormoz:iq4_nl` : `a100`, `h100` (and due to the size, it is fine on `a10g` as well.)
- `mistral-small` : `h100`
- `mistral-large` : `h100:4` (gets too expensive)
- `SIGJNF/deepseek-r1-671b-1.58bit` : `h100:4` (gets too expensive)
- `haghiri/jabir-400b:q4_k` : `h100:4` (gets too expensive)
- `gemma3:27b` : `h100`
- `gemma3:12b` : tested on `h100` but less is also possible.
- `gemma3:4b` : `a100` or `a10g` or `t4`.
- `gemma3:1b` : Basically works on CPU like a charm.
- `exaone` : `L40S`
- `exaone:32b` : `A100`
- `command-a` : `H100:4` (gets too expensive)