# Ollama 설정 변경 요약

## 변경된 파일들

### 1. `/workspace/agentic_collab/openai_config.json`
- `model-key`: "ollama"로 변경 (Ollama는 API 키가 필요하지 않음)
- `embeddings-key`: "ollama"로 변경
- `model`: "gemma3:27b-it-qat" (이미 설정되어 있음)
- `embeddings`: "nomic-embed-text:latest" (이미 설정되어 있음)

### 2. `/workspace/agentic_collab/reverie/backend_server/persona/prompt_template/gpt_structure.py`
- `setup_client` 함수의 OpenAI 클라이언트 생성 부분에 `base_url="http://172.30.1.14:11434/v1"` 추가
- 21번째 줄의 기본 클라이언트에도 base_url 추가

### 3. `/workspace/agentic_collab/reverie/backend_server/test.py`
- OpenAI 클라이언트 생성 시 `base_url="http://172.30.1.14:11434/v1"` 추가
- 모델을 "gemma3:27b-it-qat"로 변경

### 4. `/workspace/agentic_collab/nlp/openai_convo_summary.py`
- OpenAI 클라이언트 생성 시 `base_url="http://172.30.1.14:11434/v1"` 추가

## 주요 변경사항

1. **OpenAI 라이브러리 유지**: 기존 OpenAI 라이브러리를 그대로 사용하되, `base_url`을 Ollama 서버로 변경
2. **모델 설정**: 
   - 채팅 모델: `gemma3:27b-it-qat`
   - 임베딩 모델: `nomic-embed-text:latest`
3. **API 키**: Ollama는 실제 API 키가 필요하지 않으므로 "ollama"로 설정

## 연결 테스트

현재 172.30.1.14:11434에 연결할 수 없는 상태입니다. 다음을 확인해주세요:

1. Ollama 서버가 172.30.1.14:11434에서 실행되고 있는지 확인
2. 네트워크 연결 상태 확인
3. 방화벽 설정 확인

## 테스트 방법

Ollama 서버가 정상적으로 실행되면 다음 명령어로 테스트할 수 있습니다:

```bash
# 모델 목록 확인
curl http://172.30.1.14:11434/api/tags

# 채팅 테스트
curl http://172.30.1.14:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma3:27b-it-qat",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# 임베딩 테스트
curl http://172.30.1.14:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text:latest",
    "input": ["Hello world"]
  }'
```

## 다음 단계

1. Ollama 서버 연결 확인
2. 필요한 모델들이 Ollama에 설치되어 있는지 확인:
   - `ollama pull gemma3:27b-it-qat`
   - `ollama pull nomic-embed-text:latest`
3. 프로젝트 실행 및 테스트