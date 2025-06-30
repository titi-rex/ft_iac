import pulumi
import pulumi_aws as aws


class MySecurityGroup(pulumi.ComponentResource):
    """
    Security Group taking custom ingress rules
    Automatically add a "allow all" egress rule.
    Security Group = firewall
    """

    def __init__(self, name, vpc_id, rules=None, description="Security Group", opts = None):
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



        for rule in (rules or []):
            self.ingressRules.append(self.create_ingress_rule(rule["name"],
                                                              rule["ports"],
                                                              rule["protocol"]))

        self.egressRules.append(self.create_egress_rule("allow_all", 0))

        self.register_outputs(self.myOutputs)



    def create_ingress_rule(self, name, ports, protocol="tcp"):
        rule = aws.vpc.SecurityGroupIngressRule(f"{self.name}-ingress-{name}",
                                        security_group_id=self.sg.id,
                                        cidr_ipv4="0.0.0.0/0",
                                        ip_protocol="tcp",
                                        from_port=ports,
                                        to_port=ports,
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{self.name}-INngress-{name}"] = rule.id
        return rule

    def create_egress_rule(self, name, ports, protocol="-1"):
        rule = aws.vpc.SecurityGroupEgressRule(f"{self.name}-egress-{name}",
                                        security_group_id=self.sg.id,
                                        cidr_ipv4="0.0.0.0/0",
                                        ip_protocol=protocol,
                                        from_port=ports,
                                        to_port=ports,
                                        opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{self.name}-Egress-{name}"] = rule.id
        return rule
