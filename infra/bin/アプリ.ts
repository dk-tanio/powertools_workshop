import { App } from "aws-cdk-lib";
import { 書籍Apiスタック } from "../lib/書籍Apiスタック";

const app = new App();

new 書籍Apiスタック(app, "PowertoolsWorkshopBookApi");
