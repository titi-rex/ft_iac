import pulumi
import pulumi_aws as aws


class MyBucket(pulumi.ComponentResource):
    """
    S3 Bucket = store data
    Used to store codebase for deployment
    """

    def __init__(self, name, opts = None):
        """
        Create bucket object with the bundle (automatically archived)
        """

        super().__init__('ft_iac:component:bucket', name, None, opts)
        self.myOutputs = {}

        self.bucket = aws.s3.BucketV2(f"{name}-bucket",
                                      opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}BucketId"] = self.bucket.id

        bundle_asset = pulumi.FileArchive("./bundle")
        self.bucket_object = aws.s3.BucketObject(f"{name}-bundle-object",
                                                bucket=self.bucket.id,
                                                source=bundle_asset,
                                                opts=pulumi.ResourceOptions(parent=self))
        self.myOutputs[f"{name}BundleId"] = self.bucket_object.id

        self.register_outputs(self.myOutputs)
