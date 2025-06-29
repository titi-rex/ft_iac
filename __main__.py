import pulumi
import pulumi_aws as aws

config = pulumi.Config()

# [0: VPC]
"""
Virtual Private Cloud
"""
## [0.1 : Create VPC]
"""

"""
vpc = aws.ec2.Vpc("ft_iac-dev", cidr_block="10.0.0.0/16")


## [0.2 : Create subnet]
"""

"""
app_subnet = aws.ec2.Subnet("app-subnet",
                            vpc_id=vpc.id,
                            cidr_block="10.0.1.0/24",
                            availability_zone="eu-west-3a")

rds_subnet1 = aws.ec2.Subnet("rds-subnet-1",
                            vpc_id=vpc.id,
                            cidr_block="10.0.2.0/24",
                            availability_zone="eu-west-3a")

rds_subnet2 = aws.ec2.Subnet("rds-subnet-2",
                            vpc_id=vpc.id,
                            cidr_block="10.0.3.0/24",
                            availability_zone="eu-west-3b")

rds_subnet_group = aws.rds.SubnetGroup("rds-subnet-group", subnet_ids=[rds_subnet1.id, rds_subnet2.id])

## [0.2 : Create Security Group]


# Security Group for EC2 Instance allowing SSH and HTTP
app_sg = aws.ec2.SecurityGroup("app-sg", vpc_id=vpc.id, description="Enable HTTP/S and SSH access")

    # cidr_ipv6="::/0"
### [0.2.1 : Create Security Group Rule]
app_sgr_allow_ssh = aws.vpc.SecurityGroupIngressRule("app_sgr_allow_ssh",
    security_group_id=app_sg.id,
    cidr_ipv4="0.0.0.0/0",
    ip_protocol="tcp",
    from_port=22,
    to_port=22)

app_sgr_allow_http = aws.vpc.SecurityGroupIngressRule("app_sgr_allow_http",
    security_group_id=app_sg.id,
    cidr_ipv4="0.0.0.0/0",
    ip_protocol="tcp",
    from_port=80,
    to_port=80)

app_sgr_allow_https = aws.vpc.SecurityGroupIngressRule("app_sgr_allow_https",
    security_group_id=app_sg.id,
    cidr_ipv4="0.0.0.0/0",
    ip_protocol="tcp",
    from_port=443,
    to_port=443)

app_sgr_allow_all = aws.vpc.SecurityGroupEgressRule("app_sgr_allow_all",
    security_group_id=app_sg.id,
    cidr_ipv4="0.0.0.0/0",
    ip_protocol="-1")

# Security Group for RDS Instance allowing MySQL access
rds_sg = aws.ec2.SecurityGroup("rds-sg", vpc_id=vpc.id, description="Enable MySQL access from the VPC")

rds_sgr_allow_mysql = aws.vpc.SecurityGroupIngressRule("rds_sgr_allow_mysql",
    security_group_id=rds_sg.id,
    cidr_ipv4="10.0.0.0/16",
    ip_protocol="tcp",
    from_port=3306,
    to_port=3306)

rds_sgr_allow_all = aws.vpc.SecurityGroupEgressRule("rds_sgr_allow_all",
    security_group_id=rds_sg.id,
    cidr_ipv4="0.0.0.0/0",
    ip_protocol="-1")



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
# key_pair = aws.ec2.KeyPair("app-key-pair", public_key="YOUR_PUBLIC_KEY")

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

