import pulumi
import pulumi_aws as aws


class MyEc2(pulumi.ComponentResource):
    """
    EC2 = Elastic Compute Cloud 
    Compute instance for app
    """

    def __init__(self, name, sg_id, subnet_id, rds, type=aws.rds.InstanceType.T4_G_MICRO, opts = None):
        """
        Create a ec2 instance with http/s public access
        Use Amazon Linux for AMI (free)
        ami = aws.ec2.get_ami(most_recent=True, owners=["amazon"], filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}])
        """

        super().__init__('ft_iac:component:ec2', name, None, opts)
        self.myOutputs = {}

        config = pulumi.Config("ssh")
        ami_id = "ami-0f8d3c5dcfaceaa4f"


        user_data = pulumi.Output.format("""#!/bin/bash
sudo dnf update -y
sudo dnf install -y nodejs mariadb105 git
aws secretsmanager get-secret-value --secret-id {0} --query SecretString --output text >> passwd.secret
echo MYSQL_HOST={1} >> .env
echo MYSQL_USER={2} >> .env
echo MYSQL_PASSWORD=$(cat passwd.secret) >> .env
rm passwd.secret""", rds.secret.arn, rds.rds.address, rds.username)
        self.myOutputs[f"{name}user_data"] = user_data

        # Define the IAM role and policy for the EC2 instance to access the secret
        role = aws.iam.Role(f"{name}-role", 
            assume_role_policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "codedeploy.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }""",
            opts=pulumi.ResourceOptions(parent=self))

        policy = aws.iam.RolePolicy(f"{name}-policy",
            role=role.id,
            policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "secretsmanager:GetSecretValue",
                        "Resource": "*"
                    }
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:Get*",
                            "s3:List*",
                            "codedeploy:*",
                            "ec2:Describe*",
                            "iam:PassRole"
                        ],
                        "Resource": "*"
                    }
                ]
            }""",
            opts=pulumi.ResourceOptions(parent=self))

        instance_profile = aws.iam.InstanceProfile(f"{name}-instance-profile",
                                                   role=role.name,
                                                   opts=pulumi.ResourceOptions(parent=self))

        self.key_pair = aws.ec2.KeyPair(f"{name}-key-pair", 
                                        public_key=config.require("key.pub"),
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}KeyPairId"] = self.key_pair.id

        self.instance = aws.ec2.Instance(f"{name}-ec2",
                                        instance_type=aws.ec2.InstanceType.T3_MICRO,
                                        vpc_security_group_ids=[sg_id],
                                        subnet_id=subnet_id,
                                        key_name=self.key_pair.id,
                                        associate_public_ip_address=True,
                                        ami=ami_id,
                                        iam_instance_profile=instance_profile.name,
                                        user_data=user_data,
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}InstanceId"] = self.instance.id
        self.myOutputs[f"{name}InstancePubIp"] = self.instance.public_ip
        self.myOutputs[f"{name}InstancePubDns"] = self.instance.public_dns

        self.register_outputs(self.myOutputs)


"""
create key pair
disallow ssh traffic or restrict to actual ip for dev
allow http/s
set vpc
set subnet
set secgroup
inject env ?
ami = aws.get_ami(most_recent=True,
                  owners=["amazon"],
                  filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}])
"""