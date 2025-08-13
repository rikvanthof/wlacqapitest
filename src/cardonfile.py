"""Apply card-on-file data to payment requests"""
import pandas as pd
from worldline.acquiring.sdk.v1.domain.card_on_file_data import CardOnFileData
from worldline.acquiring.sdk.v1.domain.initial_card_on_file_data import InitialCardOnFileData
from worldline.acquiring.sdk.v1.domain.subsequent_card_on_file_data import SubsequentCardOnFileData

def apply_cardonfile_data(request, row, cardonfile, previous_outputs=None):
    """Apply card-on-file data to the payment request"""
    cof_id = row['card_on_file_data']
    
    # Handle both DataFrame and dict cases
    if isinstance(cardonfile, pd.DataFrame):
        if cof_id not in cardonfile.index:
            print(f"⚠️ Card-on-file ID {cof_id} not found in cardonfile DataFrame")
            return
        cof_row = cardonfile.loc[cof_id]
    elif isinstance(cardonfile, dict):
        if cof_id not in cardonfile:
            print(f"⚠️ Card-on-file ID {cof_id} not found in cardonfile dict")
            return
        cof_row = cardonfile[cof_id]
    else:
        print(f"⚠️ Unexpected cardonfile type: {type(cardonfile)}")
        return
    
    # Create CardOnFileData object
    cof_data = CardOnFileData()
    
    # Set isInitialTransaction (convert string to boolean)
    # Handle both DataFrame Series and dict access
    if isinstance(cof_row, pd.Series):
        is_initial = str(cof_row['is_initial_transaction']).lower() == 'true'
        transaction_type = cof_row['transaction_type']
        future_use = cof_row.get('future_use')
        initiator = cof_row.get('card_on_file_initiator')
    else:  # dict
        is_initial = str(cof_row.get('is_initial_transaction', '')).lower() == 'true'
        transaction_type = cof_row.get('transaction_type', '')
        future_use = cof_row.get('future_use')
        initiator = cof_row.get('card_on_file_initiator')
    
    cof_data.is_initial_transaction = is_initial
    
    if is_initial:
        # For initial transactions, create InitialCardOnFileData
        initial_data = InitialCardOnFileData()
        initial_data.transaction_type = transaction_type
        
        if future_use and pd.notna(future_use):
            initial_data.future_use = future_use
        
        cof_data.initial_card_on_file_data = initial_data
        
        print(f"🔄 Card-on-file data applied: {cof_id}, initial=True, type={initial_data.transaction_type}")
    else:
        # For subsequent transactions, create SubsequentCardOnFileData
        subsequent_data = SubsequentCardOnFileData()
        subsequent_data.transaction_type = transaction_type
        
        if initiator and pd.notna(initiator):
            subsequent_data.card_on_file_initiator = initiator
        
        # Use stored schemeTransactionId from previous COF transaction in chain
        if previous_outputs and 'scheme_transaction_id' in previous_outputs:
            subsequent_data.initial_scheme_transaction_id = previous_outputs['scheme_transaction_id']
            print(f"🔗 Using stored scheme transaction ID: {previous_outputs['scheme_transaction_id']}")
        else:
            print(f"⚠️ No scheme_transaction_id found in previous_outputs for subsequent COF transaction {cof_id}")
        
        cof_data.subsequent_card_on_file_data = subsequent_data
        
        print(f"🔄 Card-on-file data applied: {cof_id}, initial=False, type={subsequent_data.transaction_type}")
    
    # Set the card on file data on card_payment_data
    request.card_payment_data.card_on_file_data = cof_data