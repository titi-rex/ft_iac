






# [1 : S3 Bucket]
"""
Use a bucket to store codebase for deployemnt
"""
## [1.1 : Create S3 bucket]
"""
Create an S3 bucket
"""
bucket = aws.s3.BucketV2("app-bucket")


## [1.2 : Push local code to bucket]
"""
Create bucket object with the bundle (automatically archived)
"""
bundle_asset = pulumi.FileArchive("./bundle")
bucket_object = aws.s3.BucketObject("bundle-object",
    bucket=bucket.id,
    source=bundle_asset)

"""
Export name of the bucket
"""
pulumi.export('bucket_name', bucket.id)




# [2 : MySQL Database]
"""
db.t4g.micro
ssd: gp2 ou gp3
size: 20go
"""

## [2.1 : Create DB instance]
"""

"""

rds = aws.rds.Instance("app-db",
    instance_class=aws.rds.InstanceType.T4_G_MICRO,
    allocated_storage=20,
    db_name="todo_app",
    engine="mysql",
    engine_version="8.0",
    port=3306,
    username=config.get("mysql.user"),
    password=config.get_secret("mysql.password"),
    skip_final_snapshot=True,
    vpc_security_group_ids=[rds_sg.id],
    db_subnet_group_name=rds_subnet_group.name)

pulumi.export("rds_endpoint", rds.endpoint)
pulumi.export("user", config.get("mysql.user"))
pulumi.export("password", config.get_secret("mysql.password"))


# [3 : EC2 instance]
"""
create key pair
disallow ssh traffic or restrict to actual ip for dev
allow http/s
set vpc
set subnet
set secgroup
inject env ?
"""
# Create Key Pair
key_pair = aws.ec2.KeyPair("app-key-pair", public_key=config.get("key.pub"))

## [3.0 : IAM instance profile for code deploy]
""" 
IAM instance profile
"""


## [3.1 : Create instance]
"""

ami = aws.get_ami(most_recent=True,
                  owners=["amazon"],
                  filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}])
"""



user_data = """
#!/bin/bash
sudo dnf update -y
sudo dnf install node
"""

ami_id = "ami-0f8d3c5dcfaceaa4f"


# [Create an EC2 instance.]


app = aws.ec2.Instance('webapp',
    instance_type=aws.ec2.InstanceType.T3_MICRO,
    vpc_security_group_ids=[app_sg.id],
    subnet_id=app_subnet.id,
    # associate_public_ip_address=True,
    ami=ami_id)


pulumi.export('public_ipp', app.public_ip)
pulumi.export('public_host_name', app.public_dns)





# [3 : Code Deploy (https://docs.aws.amazon.com/codedeploy/latest/userguide/getting-started-policy.html)]
""" 
AWS service for deploy code from github/bucket to other aws service (here EC2 instance)
need persmission (IAM Role)
need appspec file (https://docs.aws.amazon.com/codedeploy/latest/userguide/application-revisions-appspec-file.html#add-appspec-file-server)
option script



"""
## [3.1 : Create IAM role]
"""
code deploy :
    - Role (IAM)  -> Service Role bc it's a role used by an AWS service
    - Policy -> policy attached to a role
policy needed : 
    - AWSCodeDeployRole (for EC2)
    for auto-scale groupe wit hlaunch template: 
        - ec2:RunInstances
        - ec2:CreateTags
        - iam:PassRole

"""
# IAM Role for CodeDeploy
service_role = aws.iam.Role(
    "codeDeployServiceRole",
    assume_role_policy="""{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "codedeploy.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}"""
)

### full service list for policy, remove not needed for security
"""
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    
                    "codedeploy.us-east-1.amazonaws.com",
                    "codedeploy.us-east-2.amazonaws.com",
                    "codedeploy.us-west-1.amazonaws.com",
                    "codedeploy.us-west-2.amazonaws.com",
                    "codedeploy.ca-central-1.amazonaws.com",
                    "codedeploy.ap-east-1.amazonaws.com",                  
                    "codedeploy.ap-northeast-1.amazonaws.com",
                    "codedeploy.ap-northeast-2.amazonaws.com",
                    "codedeploy.ap-northeast-3.amazonaws.com",
                    "codedeploy.ap-southeast-1.amazonaws.com",
                    "codedeploy.ap-southeast-2.amazonaws.com",
                    "codedeploy.ap-southeast-3.amazonaws.com",
                    "codedeploy.ap-southeast-4.amazonaws.com",
                    "codedeploy.ap-south-1.amazonaws.com",
                    "codedeploy.ap-south-2.amazonaws.com",
                    "codedeploy.ca-central-1.amazonaws.com",
                    "codedeploy.eu-west-1.amazonaws.com",
                    "codedeploy.eu-west-2.amazonaws.com",
                    "codedeploy.eu-west-3.amazonaws.com",
                    "codedeploy.eu-central-1.amazonaws.com",
                    "codedeploy.eu-central-2.amazonaws.com",
                    "codedeploy.eu-north-1.amazonaws.com",
                    "codedeploy.eu-south-1.amazonaws.com",
                    "codedeploy.eu-south-2.amazonaws.com",
                    "codedeploy.il-central-1.amazonaws.com",
                    "codedeploy.me-central-1.amazonaws.com",
                    "codedeploy.me-south-1.amazonaws.com",
                    "codedeploy.sa-east-1.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
"""

# Attach policy to the CodeDeploy IAM role
aws.iam.RolePolicyAttachment(
    "codeDeployServiceRoleAttachment",
    role=service_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
)


## [3.2 : Create Code Deploy App]
"""

"""

## [3.3 : Create deployement group]
"""

"""



## [3.2 : Deploy code to instance]
"""

"""
