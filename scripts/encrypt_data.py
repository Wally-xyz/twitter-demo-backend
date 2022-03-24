import sys
import boto3

ssm_client = boto3.client("ssm")
kms_client = boto3.client("kms")


def main(args):
    data_to_encrypt = args[1]
    # Whatever key you use to encrypt, same needs to be used for decrypting
    key_alias = ssm_client.get_parameter(Name=f"/prod/api/kms_db_key_alias")["Parameter"]["Value"]
    response = kms_client.encrypt(
        KeyId=key_alias,
        Plaintext=data_to_encrypt
    )
    encrypted_data = response['CiphertextBlob']
    print(f"Encrypted data in Hex Format: {encrypted_data.hex()}")

    response = kms_client.decrypt(
        KeyId=key_alias,
        CiphertextBlob=encrypted_data
    )
    print(f"Original decrypted: {response['Plaintext']}")


# Run "python ./encrypt_data.py DATA"
if __name__ == "__main__":
    main(sys.argv)
