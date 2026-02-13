FROM public.ecr.aws/lambda/python:3.14

# 依存関係のインストール
COPY infra/docker/requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# アプリケーションコードをコピー
COPY src ${LAMBDA_TASK_ROOT}

CMD ["handler.lambda_handler"]
