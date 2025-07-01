import pulumi
import pulumi_aws as aws


class MySecurityGroup(pulumi.ComponentResource):
    """
    Security Group taking custom ingress rules
    Automatically add a "allow all" egress rule.
    Security Group = firewall
    """

    def __init__(self, name, vpc_id, description="Security Group", opts = None):
        super().__init__('ft_iac:component:sg', f"{name}-sg", None, opts)
        self.name = f"{name}-sg"
        self.myOutputs = {}
        self.ingressRules = []
        self.egressRules = []
        
        self.sg = aws.ec2.SecurityGroup(f"{name}-sg",
                                        vpc_id=vpc_id,
                                        description=description,
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}SgId"] = self.sg.id

        self.register_outputs(self.myOutputs)


    def create_ingress_rule(self, name, from_port, cidr_ipv4=None, referenced_security_group_id=None, to_port=None, protocol="tcp"):
        if cidr_ipv4 and referenced_security_group_id:
            raise RuntimeError(f"{self.name}: set cidr_ipv4 or sg_id")
        rule = aws.vpc.SecurityGroupIngressRule(f"{self.name}-ingress-{name}",
                                        security_group_id=self.sg.id,
                                        cidr_ipv4=cidr_ipv4,
                                        referenced_security_group_id=referenced_security_group_id,
                                        ip_protocol=protocol,
                                        from_port=from_port,
                                        to_port=to_port or from_port,
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{self.name}-Ingress-{name}"] = rule.id
        self.ingressRules.append(rule)

    def create_egress_rule(self, name, from_port, cidr_ipv4=None, referenced_security_group_id=None, to_port=None, protocol="tcp"):
        rule = aws.vpc.SecurityGroupEgressRule(f"{self.name}-egress-{name}",
                                        security_group_id=self.sg.id,
                                        cidr_ipv4=cidr_ipv4,
                                        referenced_security_group_id=referenced_security_group_id,
                                        ip_protocol=protocol,
                                        from_port=from_port,
                                        to_port=to_port or from_port,
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{self.name}-Egress-{name}"] = rule.id
        self.egressRules.append(rule)

