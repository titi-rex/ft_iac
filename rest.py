





# Internet Gateway

# Route Table


# Route Table Association








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
