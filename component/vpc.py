import pulumi
import pulumi_aws as aws
from component.sg import MySecurityGroup

# add IGW 
# add route 0000 -> igw 
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

        # Create IGW 
        self.igw = aws.ec2.InternetGateway(f"{name}-igw", vpc_id=self.vpc.id,
                                           opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs["igwId"] = self.igw.id

        # Create subnets
        self.publicSubnets = self.create_subnet(name="app", number=1)
        self.privateSubnets = self.create_subnet(name="rds", number=2, cidr_offset=2)
        self.privateSubnetsGroup = aws.rds.SubnetGroup("rds-subnet-group", 
                                        subnet_ids=[sb.id for sb in self.privateSubnets],
                                        opts=pulumi.ResourceOptions(parent=self.vpc))
        self.myOutputs["subnetGroupId"] =  self.privateSubnetsGroup.id

        # Create and configure Security Group
        self.appSecurityGroup = MySecurityGroup("app",
                                             self.vpc.id,
                                             description="Security Group for public app instance",
                                             opts=pulumi.ResourceOptions(parent=self))
        self.appSecurityGroup.create_ingress_rule("allow_ssh", 
                                                  22, 
                                                  cidr_ipv4="0.0.0.0/0")
        self.appSecurityGroup.create_ingress_rule("allow_http", 
                                                  80,
                                                  cidr_ipv4="0.0.0.0/0")
        self.appSecurityGroup.create_egress_rule("allow_all",
                                                 0, 
                                                 cidr_ipv4="0.0.0.0/0",
                                                 protocol="-1")
        
        self.rdsSecurityGroup = MySecurityGroup("rds",
                                                self.vpc.id,
                                                description="Security Group for private RDS instance",
                                                opts=pulumi.ResourceOptions(parent=self))
        self.rdsSecurityGroup.create_ingress_rule("allow_mysql", 
                                                  3306, 
                                                  cidr_ipv4="0.0.0.0/0")
        self.rdsSecurityGroup.create_egress_rule("allow_all", 
                                                  0, 
                                                  referenced_security_group_id=self.appSecurityGroup.sg.id,
                                                  protocol="-1")


        self.rt = aws.ec2.RouteTable(f"{name}-rt-toigw",
                                    vpc_id=self.vpc.id,
                                    routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": self.igw.id}],
                                    opts=pulumi.ResourceOptions(parent=self))
        rta = aws.ec2.RouteTableAssociation(f"{name}-route-table-association",
                                            subnet_id=self.publicSubnets[0].id,
                                            route_table_id=self.rt.id,
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
                            opts=pulumi.ResourceOptions(parent=self.vpc)))
            self.myOutputs[f"{name}Subnet{i}Id"] =  subnet[i].id
        return subnet
