import pulumi
import pulumi_aws as aws
from component.vpc import MyVpc

config = pulumi.Config()

vpc = MyVpc("app-myvpc")

pulumi.export("vpcOutput", vpc.myOutputs)
pulumi.export("appSgOutput", vpc.appSecurityGroup.myOutputs)
pulumi.export("rdsSgOutput", vpc.rdsSecurityGroup.myOutputs)

