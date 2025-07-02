import pulumi
import pulumi_aws as aws
from component.vpc import MyVpc
from component.bucket import MyBucket
from component.rds import MyRds
from component.ec2 import MyEc2
from component.codedeploy import MyCodeDeploy

config = pulumi.Config()

vpc = MyVpc("app-myvpc")

pulumi.export("vpcOutput", vpc.myOutputs)
pulumi.export("sgAppOutput", vpc.appSecurityGroup.myOutputs)
pulumi.export("sgRdsOutput", vpc.rdsSecurityGroup.myOutputs)

bucket = MyBucket("app-mybucket")
pulumi.export("bucketOutput", bucket.myOutputs)

rds = MyRds("app-myrds",
            vpc.rdsSecurityGroup.sg.id,
            vpc.privateSubnetsGroup.id,
            db_name="todo_app")
pulumi.export("rdsOutput", rds.myOutputs)

app = MyEc2("app-myec2",
            vpc.appSecurityGroup.sg.id,
            vpc.publicSubnets[0].id,
            rds=rds)
pulumi.export("ec2Output", app.myOutputs)

cd_app = MyCodeDeploy("app-cd")


pulumi.export("codedeployOutput", cd_app.myOutputs)