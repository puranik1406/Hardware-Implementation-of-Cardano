{-# LANGUAGE DataKinds #-}
{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE TypeApplications #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE NoImplicitPrelude #-}

module PaymentContract where

import qualified PlutusTx
import PlutusTx.Prelude
import Plutus.V2.Ledger.Api
import Plutus.V2.Ledger.Contexts
import qualified Plutus.Script.Utils.V2.Typed.Scripts as Scripts
import qualified Data.ByteString.Lazy as LBS
import qualified Data.ByteString.Short as SBS
import Codec.Serialise

-- | Payment contract datum - stores payment information
data PaymentDatum = PaymentDatum
    { sender :: PubKeyHash
    , recipient :: PubKeyHash
    , amount :: Integer
    , paymentId :: BuiltinByteString
    , status :: PaymentStatus
    } deriving Show

-- | Payment status enumeration
data PaymentStatus = Pending | Confirmed | Cancelled
    deriving Show

-- | Payment redeemer - actions that can be performed
data PaymentRedeemer = 
    ExecutePayment
    | CancelPayment
    | ConfirmPayment
    deriving Show

-- Make instances for Plutus
PlutusTx.unstableMakeIsData ''PaymentDatum
PlutusTx.unstableMakeIsData ''PaymentStatus
PlutusTx.unstableMakeIsData ''PaymentRedeemer

-- | Validator function for the payment contract
{-# INLINABLE paymentValidator #-}
paymentValidator :: PaymentDatum -> PaymentRedeemer -> ScriptContext -> Bool
paymentValidator datum redeemer ctx =
    case redeemer of
        ExecutePayment -> validateExecutePayment datum ctx
        CancelPayment -> validateCancelPayment datum ctx
        ConfirmPayment -> validateConfirmPayment datum ctx

-- | Validate payment execution
{-# INLINABLE validateExecutePayment #-}
validateExecutePayment :: PaymentDatum -> ScriptContext -> Bool
validateExecutePayment datum ctx =
    traceIfFalse "Payment already processed" (status datum == Pending) &&
    traceIfFalse "Insufficient payment amount" (checkPaymentAmount datum ctx) &&
    traceIfFalse "Invalid recipient" (checkRecipientOutput datum ctx) &&
    traceIfFalse "Transaction not signed by sender" (txSignedBy info (sender datum))
  where
    info = scriptContextTxInfo ctx

-- | Validate payment cancellation
{-# INLINABLE validateCancelPayment #-}
validateCancelPayment :: PaymentDatum -> ScriptContext -> Bool
validateCancelPayment datum ctx =
    traceIfFalse "Only sender can cancel" (txSignedBy info (sender datum)) &&
    traceIfFalse "Payment already processed" (status datum == Pending)
  where
    info = scriptContextTxInfo ctx

-- | Validate payment confirmation
{-# INLINABLE validateConfirmPayment #-}
validateConfirmPayment :: PaymentDatum -> ScriptContext -> Bool
validateConfirmPayment datum ctx =
    traceIfFalse "Only recipient can confirm" (txSignedBy info (recipient datum)) &&
    traceIfFalse "Payment not pending" (status datum == Pending)
  where
    info = scriptContextTxInfo ctx

-- | Check if payment amount is correct
{-# INLINABLE checkPaymentAmount #-}
checkPaymentAmount :: PaymentDatum -> ScriptContext -> Bool
checkPaymentAmount datum ctx =
    let
        info = scriptContextTxInfo ctx
        outputs = txInfoOutputs info
        recipientOutputs = filter (isRecipientOutput (recipient datum)) outputs
        totalPaid = sum $ map (getLovelace . txOutValue) recipientOutputs
    in
        totalPaid >= amount datum

-- | Check if recipient receives correct output
{-# INLINABLE checkRecipientOutput #-}
checkRecipientOutput :: PaymentDatum -> ScriptContext -> Bool
checkRecipientOutput datum ctx =
    let
        info = scriptContextTxInfo ctx
        outputs = txInfoOutputs info
        recipientOutputs = filter (isRecipientOutput (recipient datum)) outputs
    in
        not (null recipientOutputs)

-- | Helper to check if output goes to recipient
{-# INLINABLE isRecipientOutput #-}
isRecipientOutput :: PubKeyHash -> TxOut -> Bool
isRecipientOutput pkh txOut =
    case txOutAddress txOut of
        Address (PubKeyCredential pkh') _ -> pkh == pkh'
        _ -> False

-- | Extract lovelace amount from Value
{-# INLINABLE getLovelace #-}
getLovelace :: Value -> Integer
getLovelace v = valueOf v adaSymbol adaToken

-- | Typed validator wrapper
data PaymentContract
instance Scripts.ValidatorTypes PaymentContract where
    type instance DatumType PaymentContract = PaymentDatum
    type instance RedeemerType PaymentContract = PaymentRedeemer

-- | Compile the validator
typedValidator :: Scripts.TypedValidator PaymentContract
typedValidator = Scripts.mkTypedValidator @PaymentContract
    $$(PlutusTx.compile [|| paymentValidator ||])
    $$(PlutusTx.compile [|| wrap ||])
  where
    wrap = Scripts.mkUntypedValidator @PaymentDatum @PaymentRedeemer

-- | Get the validator script
validator :: Validator
validator = Scripts.validatorScript typedValidator

-- | Get the validator hash
validatorHash :: ValidatorHash
validatorHash = Scripts.validatorHash typedValidator

-- | Get the script address
scriptAddress :: Address
scriptAddress = scriptHashAddress validatorHash

-- | Serialise the validator for use in transactions
validatorScript :: PlutusScript PlutusScriptV2
validatorScript = PlutusScriptSerialised
    $ SBS.toShort
    $ LBS.toStrict
    $ serialise validator