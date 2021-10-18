# Easy Peasy Web Server

For when you need to spin up a sample webserver, but you gotta do it "proper".

Here's the architecture setup. There is also a CFN and CDK script to do it for you.

## Deployment

### CloudFormation

You can deploy CFN templates through the console, or using the CLI
`aws cloudformation deploy --template-file web-server-cf.yaml --stack-name <your-stack-name> --capabilities CAPABILITY_IAM`