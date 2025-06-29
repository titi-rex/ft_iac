import pulumi
import pulumi_aws as aws
import pulumi_mysql as mysql



# Create a MySQL database
mysql_db = mysql.Database("my-mysql-db",
    name="mydatabase")

# Create a new VPC
vpc = aws.ec2.Vpc(
    "my-vpc",
    cidr_block="10.0.0.0/16",
    tags={
        "Name": "my-vpc",
    },
)

# Create a new Subnet in the VPC
subnet = aws.ec2.Subnet(
    "my-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    tags={
        "Name": "my-subnet",
    },
)

# Find Debian-based AMI
ami_id = aws.ec2.get_ami(
    most_recent=True,
    owners=["136693071363"],  # This is the account ID for Debian AMIs
    filters=[{
        "name": "name",
        "values": ["debian-stretch-hvm-x86_64-gp2-*"],
    }]
).id

# User data script to update packages and install Node.js
user_data_script = """#!/bin/bash
# Update packages and install curl
apt-get update -y
apt-get install -y curl

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
apt-get install -y nodejs
"""

# Create an EC2 instance in the VPC using Debian-based AMI and install Node.js
instance = aws.ec2.Instance(
    "my-instance",
    instance_type="t2.micro",
    vpc_security_group_ids=[vpc.default_security_group.id],
    ami=ami_id,
    subnet_id=subnet.id,
    user_data=user_data_script,
    tags={
        "Name": "my-instance",
    },
)

# CodeDeploy Application
codedeploy_app = aws.codedeploy.Application(
    "my-codedeploy-app",
    compute_platform="Server",
    tags={
        "Name": "my-codedeploy-app",
    }
)



# CodeDeploy Deployment Group
deployment_group = aws.codedeploy.DeploymentGroup(
    "my-deployment-group",
    app_name=codedeploy_app.name,
    service_role_arn=service_role.arn,
    deployment_group_name="my-deployment-group",
    ec2_tag_filters=[{
        "key": "Name",
        "value": "my-instance",
        "type": "KEY_AND_VALUE",
    }],
    deployment_style={
        "deploymentType": "IN_PLACE",
        "deploymentOption": "WITHOUT_HEALTH_CHECK"
    },
    tags={
        "Name": "my-deployment-group",
    }
)

# Export the IDs and URLs of the created resources
pulumi.export("vpc_id", vpc.id)
pulumi.export("subnet_id", subnet.id)
pulumi.export("instance_id", instance.id)
pulumi.export("bucket_name", bucket.bucket)
pulumi.export("mysql_db_name", mysql_db.name)
pulumi.export("codedeploy_app_name", codedeploy_app.name)
pulumi.export("deployment_group_name", deployment_group.deployment_group_name)
pulumi.export("source_bucket_url", bucket.bucket.apply(lambda bucket_name: f"s3://{bucket_name}/"))

















import pulumi
import pulumi_aws as aws

# Create a VPC
vpc = aws.ec2.Vpc("my_vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "my_vpc"})

# Create Subnets
subnets = [
    aws.ec2.Subnet(f"my_subnet_{i}",
        vpc_id=vpc.id,
        cidr_block=f"10.0.{i}.0/24",
        availability_zone=f"{zone}",
        tags={"Name": f"my_subnet_{i}"})
    for i, zone in enumerate(['us-west-2a', 'us-west-2b'])
]

# Create an Internet Gateway
igw = aws.ec2.InternetGateway("my_igw",
    vpc_id=vpc.id,
    tags={"Name": "my_igw"})

# Create Route Table and a route for the Internet Gateway
route_table = aws.ec2.RouteTable("my_route_table",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
    )],
    tags={"Name": "my_route_table"})

# Associate Subnets with Route Table
route_table_associations = [
    aws.ec2.RouteTableAssociation(f"my_rtab_assoc_{i}",
        subnet_id=subnet.id,
        route_table_id=route_table.id)
    for i, subnet in enumerate(subnets)
]

# Create Security Group
security_group = aws.ec2.SecurityGroup("my_sg",
    vpc_id=vpc.id,
    description="Allow all inbound traffic",
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        protocol="-1",
        from_port=0,
        to_port=0,
        cidr_blocks=["0.0.0.0/0"],
    )],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        protocol="-1",
        from_port=0,
        to_port=0,
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={"Name": "my_sg"})

# Create EC2 Instances
instances = [
    aws.ec2.Instance(f"my_instance_{i}",
        ami="ami-0c55b159cbfafe1f0",  # Amazon Linux 2 AMI
        instance_type="t2.micro",
        subnet_id=subnet.id,
        vpc_security_group_ids=[security_group.id],
        tags={"Name": f"my_instance_{i}"})
    for i, subnet in enumerate(subnets)
]

# Create an Application Load Balancer
alb = aws.lb.LoadBalancer("my_alb",
    internal=False,
    security_groups=[security_group.id],
    subnets=[subnet.id for subnet in subnets],
    tags={"Name": "my_alb"})

# Create a Target Group
target_group = aws.lb.TargetGroup("my_target_group",
    port=80,
    protocol="HTTP",
    target_type="instance",
    vpc_id=vpc.id,
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        interval=30,
        path="/",
        port="80",
        protocol="HTTP",
    ))

# Attach EC2 instances to the Target Group
target_group_attachments = [
    aws.lb.TargetGroupAttachment(f"tg_attachment_{i}",
        target_group_arn=target_group.arn,
        target_id=instance.id,
        port=80)
    for i, instance in enumerate(instances)
]

# Create a Listener
listener = aws.lb.Listener("my_listener",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[aws.lb.ListenerDefaultActionArgs(
        type="forward",
        target_group_arn=target_group.arn
    )])

# Create an RDS MySQL instance
db_subnet_group = aws.rds.SubnetGroup("my_db_subnet_group",
    subnet_ids=[subnet.id for subnet in subnets],
    tags={"Name": "my_db_subnet_group"})

db = aws.rds.Instance("my_db",
    allocated_storage=20,
    engine="mysql",
    engine_version="8.0",
    instance_class="db.t2.micro",
    db_subnet_group_name=db_subnet_group.name,
    vpc_security_group_ids=[security_group.id],
    skip_final_snapshot=True,
    name="mydb",
    username="admin",
    password="password")

# Export the DNS name of the load balancer
pulumi.export("alb_dns_name", alb.dns_name)
pulumi.export("db_instance_endpoint", db.endpoint)
