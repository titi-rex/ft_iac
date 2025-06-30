import pulumi
import pulumi_aws as aws
from component.sg import MySecurityGroup


# [VPC]
class MyVpc(pulumi.ComponentResource):
    """
    VPC = Virtual Private Cloud
    Used to isolate ressource in AWS
    """

    def __init__(self, name, opts = None):
        super().__init__('ft_iac:component:vpc', name, None, opts)
        self.myOutputs = {}

        self.vpc = aws.ec2.Vpc(f"{name}-vpc", 
                                    cidr_block="10.0.0.0/16", 
                                    opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs["vpcId"] = self.vpc.id


        self.publicSubnets = self.create_subnet(name="app", number=1)
        self.privateSubnets = self.create_subnet(name="rds", number=2, cidr_offset=2)

        self.privateSubnetsGroup = aws.rds.SubnetGroup("rds-subnet-group", 
                                        subnet_ids=[sb.id for sb in self.privateSubnets],
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs["subnetGroupId"] =  self.privateSubnetsGroup.id


        rules = [
            {
                "name": "allow_ssh",
                "ports": 22,
                "protocol": "tcp",
             },
            {
                "name": "allow_http",
                "ports": 80,
                "protocol": "tcp",
             },
            {
                "name": "allow_https",
                "ports": 443,
                "protocol": "tcp",
             }
        ]

        self.appSecurityGroup = MySecurityGroup("app",
                                             self.vpc.id,
                                             rules=rules,
                                             description="Security Group for public app instance",
                                             opts=pulumi.ResourceOptions(parent=self))
        
        rules = [
            {
                "name": "allow_mysql",
                "ports": 3306,
                "protocol": "tcp",
             }
        ]

        self.rdsSecurityGroup = MySecurityGroup("rds",
                                             self.vpc.id,
                                             rules=rules,
                                             description="Security Group for private RDS instance",
                                             opts=pulumi.ResourceOptions(parent=self))

        self.register_outputs(self.myOutputs)


    def create_subnet(self, name, number=2, cidr_offset=1, region="eu-west-3"):
        if number > 3:
            raise RuntimeError(f"More than 3 AZ asked for region {region}.")
        suffix = ['a', 'b', 'c']
        subnet = []
        for i in range(0, number):
            subnet.append(aws.ec2.Subnet(f"{name}-subnet-{i+1}",
                            vpc_id=self.vpc.id,
                            cidr_block=f"10.0.{cidr_offset+i}.0/24",
                            availability_zone=f"{region}{suffix[i]}",
                            opts=pulumi.ResourceOptions(parent=self)))
            self.myOutputs[f"{name}Subnet{i}Id"] =  subnet[i].id
        return subnet

