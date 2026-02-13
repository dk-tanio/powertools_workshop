import { Duration, RemovalPolicy, Stack, StackProps } from "aws-cdk-lib";
import { Cors, LambdaIntegration, RestApi } from "aws-cdk-lib/aws-apigateway";
import { AttributeType, BillingMode, Table } from "aws-cdk-lib/aws-dynamodb";
import { Platform } from "aws-cdk-lib/aws-ecr-assets";
import { ServicePrincipal } from "aws-cdk-lib/aws-iam";
import { Architecture, DockerImageCode, DockerImageFunction } from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";

export class 書籍Apiスタック extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const 書籍テーブル = new Table(this, "BooksTable", {
      partitionKey: { name: "id", type: AttributeType.STRING },
      billingMode: BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const 書籍Api関数 = new DockerImageFunction(this, "BooksApiFunction", {
      code: DockerImageCode.fromImageAsset("..", {
        file: "infra/docker/Dockerfile",
        platform: Platform.LINUX_AMD64,
      }),
      architecture: Architecture.X86_64,
      timeout: Duration.seconds(10),
      memorySize: 256,
      environment: {
        BOOKS_TABLE_NAME: 書籍テーブル.tableName,
      },
    });

    書籍テーブル.grantReadWriteData(書籍Api関数);

    const 書籍Api = new RestApi(this, "BooksApi", {
      restApiName: "PowertoolsWorkshopBooksApi",
      cloudWatchRole: false,
      defaultCorsPreflightOptions: {
        allowOrigins: Cors.ALL_ORIGINS,
        allowMethods: Cors.ALL_METHODS,
        allowHeaders: [
          "Access-Control-Allow-Headers",
          "Origin",
          "Accept",
          "X-Requested-With",
          "Content-Type",
          "Access-Control-Request-Method",
          "Access-Control-Request-Headers",
          "Authorization",
        ],
      },
    });

    const 統合 = new LambdaIntegration(書籍Api関数, { proxy: true });
    書籍Api.root.addProxy({ defaultIntegration: 統合 });

    書籍Api関数.addPermission("AllowInvokeFromApiGateway", {
      principal: new ServicePrincipal("apigateway.amazonaws.com"),
      sourceArn: 書籍Api.arnForExecuteApi("*", "/*", "*"),
    });
  }
}
