import pulumi
import pulumi_aws as aws


class MyRds(pulumi.ComponentResource):
    """
    RDS = Relational Database Service
    Database for app
    """

    def __init__(self, name, sg_id, sbg_name, db_name="todo_app", type=aws.rds.InstanceType.T4_G_MICRO, opts = None):
        """
        Create a mysql database with 20go storage
        """

        super().__init__('ft_iac:component:rds', name, None, opts)
        self.myOutputs = {}
        config = pulumi.Config("database")


        self.secret = aws.secretsmanager.Secret(f"{name}-secret",
                                           opts=pulumi.ResourceOptions(parent=self))
        secret_version = aws.secretsmanager.SecretVersion(f"{name}-secret-version",
            secret_id=self.secret.id,
            secret_string=config.require_secret("password"),
            opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}SecretArn"] = self.secret.arn

        self.rds = aws.rds.Instance(f"{name}-rds",
                                    instance_class=type,
                                    allocated_storage=20,
                                    db_name=db_name,
                                    engine="mysql",
                                    engine_version="8.0",
                                    port=3306,
                                    username=config.require("user"),
                                    password=config.require_secret("password"),
                                    skip_final_snapshot=True,
                                    vpc_security_group_ids=[sg_id],
                                    db_subnet_group_name=sbg_name,
                                    opts=pulumi.ResourceOptions(parent=self))

        self.username = config.require("user")

        self.myOutputs[f"{name}RdsId"] = self.rds.id
        self.myOutputs[f"{name}RdsEndpoint"] = self.rds.endpoint
        self.myOutputs[f"{name}RdsAddress"] = self.rds.address
        self.myOutputs[f"{name}RdsUser"] = self.rds.username
        self.myOutputs[f"{name}RdsPassword"] = self.rds.password
        self.myOutputs[f"{name}ConfigUser"] = config.require("user")
        self.myOutputs[f"{name}ConfigPassword"] = config.require_secret("password")

        self.register_outputs(self.myOutputs)
