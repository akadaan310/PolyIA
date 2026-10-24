#!/usr/bin/env python3
"""Read-only instance-principal ingress preflight; never print credential material.

Run with the official OCI SDK installed in a separate operator environment.
This script does not change cloud resources, firewall rules, or application state.
"""
import json
import signal
import urllib.request


def metadata(path):
    request = urllib.request.Request('http://169.254.169.254/opc/v2/' + path,
                                     headers={'Authorization': 'Bearer Oracle'})
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


def probe():
    import oci

    result = {'sdk_version': oci.__version__, 'operations': []}
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner(
            federation_client_retry_strategy=oci.retry.NoneRetryStrategy(), log_requests=False)
    except Exception as error:
        result['authentication'] = {'status': 'UNAVAILABLE', 'error_type': type(error).__name__,
                                    'http_status': getattr(error, 'status', None),
                                    'code': getattr(error, 'code', None)}
        return result
    result['authentication'] = {'status': 'AVAILABLE', 'region': signer.region}
    client = oci.core.VirtualNetworkClient({}, signer=signer, timeout=(5, 10),
                                           retry_strategy=oci.retry.NoneRetryStrategy())
    for vnic in metadata('vnics/'):
        operation = {'operation': 'get_vnic', 'vnic_id': vnic['vnicId']}
        try:
            response = client.get_vnic(vnic['vnicId'])
            operation.update(status='PASS', subnet_id=response.data.subnet_id,
                             nsg_ids=response.data.nsg_ids)
        except Exception as error:
            operation.update(status='UNAVAILABLE', error_type=type(error).__name__,
                             http_status=getattr(error, 'status', None), code=getattr(error, 'code', None))
        result['operations'].append(operation)
    return result


if __name__ == '__main__':
    def timeout(_signal, _frame):
        raise TimeoutError('bounded operator probe')

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(45)
    try:
        result = probe()
    except Exception as error:
        result = {'status': 'UNAVAILABLE', 'error_type': type(error).__name__}
    finally:
        signal.alarm(0)
    print(json.dumps(result, indent=2, sort_keys=True))
