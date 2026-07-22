#1. DynamoDB table    → stores incidents
#2. SNS topic         → sends alerts to security
#3. Lambda function   → runs lambda_handler.py
#4. IoT Core          → receives fog node alerts