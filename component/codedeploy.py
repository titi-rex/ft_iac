import pulumi
import pulumi_aws as aws


class MyCodeDeploy(pulumi.ComponentResource):
    """
    CodeDeploy = deployment service
    Push code to ec2 instance
    """

    def __init__(self, name, opts = None):
        """
        Create a CodeDeploy app 
        """

        super().__init__('ft_iac:component:cdeploy', name, None, opts)
        self.myOutputs = {}

        self.role = aws.iam.Role(f"{name}-role",
                    assume_role_policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "codedeploy.amazonaws.com"
                            ]
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }""",
            opts=pulumi.ResourceOptions(parent=self))

        policy = aws.iam.RolePolicyAttachment(f"{name}-policy",
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole",
            role=self.role.name,
            opts=pulumi.ResourceOptions(parent=self))


        self.app = aws.codedeploy.Application(f"{name}-codedeploy-app", 
                                              compute_platform="Server",
                                              opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}AppNAme"] = self.app.name
        
        self.group = aws.codedeploy.DeploymentGroup(f"{name}-deployment-group",
                                                    app_name=self.app.name,
                                                    deployment_group_name=f"{name}-deployment-group",
                                                    service_role_arn=self.role.arn,
                                                    ec2_tag_filters=[{
                                                        "type": "KEY_AND_VALUE",
                                                        "key": "type",
                                                        "value": "app-instance-cd",
                                                    }],
                                                    auto_rollback_configuration={
                                                        "enabled": True,
                                                        "events": ["DEPLOYMENT_FAILURE"],
                                                    },
                                                    outdated_instances_strategy="UPDATE",
                                                    opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}GroupeId"] = self.group.id
