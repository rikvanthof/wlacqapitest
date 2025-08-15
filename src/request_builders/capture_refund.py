"""Build requests for capture refund API calls"""
import pandas as pd
import datetime
from worldline.acquiring.sdk.v1.domain.api_capture_request_for_refund import ApiCaptureRequestForRefund
from worldline.acquiring.sdk.v1.domain.payment_references import PaymentReferences
from ..utils import generate_random_string, clean_request

def build_capture_refund_request(row):
    """Build ApiCaptureRequestForRefund for capture refund calls"""
    request = ApiCaptureRequestForRefund()

    # Create References object first
    references = PaymentReferences()

    if pd.notna(row.get('dynamic_descriptor')):
        references.dynamic_descriptor = row['dynamic_descriptor']

    # Set required fields
    request.operation_id = row['test_id'] + ':' + generate_random_string(32)
    references.merchant_reference = row['test_id'] + ':' + generate_random_string(32)
    request.transaction_timestamp = pd.Timestamp.now(tz=datetime.timezone.utc).replace(microsecond=0).to_pydatetime()

    # Assign references to request
    request.references = references

    return clean_request(request)