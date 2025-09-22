{-# LANGUAGE DataKinds #-}
{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE TypeApplications #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE NoImplicitPrelude #-}

module ArduinoPaymentContract where

import qualified PlutusTx
import PlutusTx.Prelude
import Plutus.V2.Ledger.Api
import Plutus.V2.Ledger.Contexts
import qualified Plutus.Script.Utils.V2.Typed.Scripts as Scripts
import qualified Data.ByteString.Lazy as LBS
import qualified Data.ByteString.Short as SBS
import Codec.Serialise

-- | Arduino payment contract datum - stores payment information
data ArduinoPaymentDatum = ArduinoPaymentDatum
    { apSender :: PubKeyHash           -- Agent A (buyer)
    , apRecipient :: PubKeyHash        -- Agent B (seller)
    , apAmount :: Integer              -- Amount in lovelace
    , apPaymentId :: BuiltinByteString -- Unique payment identifier
    , apProductInfo :: BuiltinByteString -- Product/service description
    , apArduinoSignature :: BuiltinByteString -- Arduino device signature
    , apStatus :: PaymentStatus        -- Current payment status
    , apTimestamp :: Integer           -- Creation timestamp
    } deriving Show

-- | Payment status enumeration
data PaymentStatus = 
    Pending       -- Payment initiated but not confirmed
    | Confirmed   -- Payment confirmed by both parties
    | Cancelled   -- Payment cancelled
    | Disputed    -- Payment under dispute
    deriving Show

-- | Arduino payment redeemer - actions that can be performed
data ArduinoPaymentRedeemer = 
    ExecutePayment                     -- Execute the payment
    | ConfirmPayment                   -- Confirm payment receipt
    | CancelPayment                    -- Cancel the payment
    | DisputePayment BuiltinByteString -- Dispute with reason
    | ResolveDispute Bool              -- Resolve dispute (True = favor sender)
    deriving Show

-- Make instances for Plutus
PlutusTx.unstableMakeIsData ''ArduinoPaymentDatum
PlutusTx.unstableMakeIsData ''PaymentStatus
PlutusTx.unstableMakeIsData ''ArduinoPaymentRedeemer

-- | Validator function for the Arduino payment contract
{-# INLINABLE arduinoPaymentValidator #-}
arduinoPaymentValidator :: ArduinoPaymentDatum -> ArduinoPaymentRedeemer -> ScriptContext -> Bool
arduinoPaymentValidator datum redeemer ctx =
    case redeemer of
        ExecutePayment -> validateExecutePayment datum ctx
        ConfirmPayment -> validateConfirmPayment datum ctx
        CancelPayment -> validateCancelPayment datum ctx
        DisputePayment reason -> validateDisputePayment datum reason ctx
        ResolveDispute resolution -> validateResolveDispute datum resolution ctx

-- | Validate payment execution
{-# INLINABLE validateExecutePayment #-}
validateExecutePayment :: ArduinoPaymentDatum -> ScriptContext -> Bool
validateExecutePayment datum ctx =
    traceIfFalse "Payment already processed" (apStatus datum == Pending) &&
    traceIfFalse "Insufficient payment amount" checkPaymentAmount &&
    traceIfFalse "Invalid sender signature" checkSenderSignature &&
    traceIfFalse "Arduino signature required" checkArduinoSignature
  where
    info :: TxInfo
    info = scriptContextTxInfo ctx
    
    checkPaymentAmount :: Bool
    checkPaymentAmount = 
        let paidToRecipient = valuePaidTo info (apRecipient datum)
            requiredAmount = lovelaceValueOf (apAmount datum)
        in paidToRecipient `geq` requiredAmount
    
    checkSenderSignature :: Bool
    checkSenderSignature = txSignedBy info (apSender datum)
    
    checkArduinoSignature :: Bool
    checkArduinoSignature = 
        -- In a real implementation, this would verify the Arduino device signature
        -- For now, we just check that a signature is present
        apArduinoSignature datum /= ""

-- | Validate payment confirmation
{-# INLINABLE validateConfirmPayment #-}
validateConfirmPayment :: ArduinoPaymentDatum -> ScriptContext -> Bool
validateConfirmPayment datum ctx =
    traceIfFalse "Payment not executed yet" (apStatus datum == Pending) &&
    traceIfFalse "Only recipient can confirm" checkRecipientSignature &&
    traceIfFalse "Must update status to confirmed" checkStatusUpdate
  where
    info :: TxInfo
    info = scriptContextTxInfo ctx
    
    checkRecipientSignature :: Bool
    checkRecipientSignature = txSignedBy info (apRecipient datum)
    
    checkStatusUpdate :: Bool
    checkStatusUpdate = 
        -- Check that output datum has status updated to Confirmed
        case getContinuingOutputs ctx of
            [o] -> case txOutDatum o of
                OutputDatum (Datum d) -> 
                    case PlutusTx.fromBuiltinData d of
                        Just newDatum -> apStatus newDatum == Confirmed
                        Nothing -> False
                _ -> False
            _ -> False

-- | Validate payment cancellation
{-# INLINABLE validateCancelPayment #-}
validateCancelPayment :: ArduinoPaymentDatum -> ScriptContext -> Bool
validateCancelPayment datum ctx =
    traceIfFalse "Payment already processed" (apStatus datum == Pending) &&
    traceIfFalse "Only sender can cancel" checkSenderSignature &&
    traceIfFalse "Cancellation window expired" checkCancellationWindow
  where
    info :: TxInfo
    info = scriptContextTxInfo ctx
    
    checkSenderSignature :: Bool
    checkSenderSignature = txSignedBy info (apSender datum)
    
    checkCancellationWindow :: Bool
    checkCancellationWindow = 
        -- Allow cancellation within 1 hour (3600000 milliseconds)
        let currentTime = case ivTo (txInfoValidRange info) of
                UpperBound (Finite t) _ -> t
                _ -> 0  -- If no upper bound, allow cancellation
            creationTime = apTimestamp datum
            timeDiff = currentTime - creationTime
        in timeDiff <= 3600000

-- | Validate payment dispute
{-# INLINABLE validateDisputePayment #-}
validateDisputePayment :: ArduinoPaymentDatum -> BuiltinByteString -> ScriptContext -> Bool
validateDisputePayment datum reason ctx =
    traceIfFalse "Payment not in valid state for dispute" validStateForDispute &&
    traceIfFalse "Only involved parties can dispute" checkInvolvedParty &&
    traceIfFalse "Dispute reason required" (reason /= "") &&
    traceIfFalse "Must update status to disputed" checkDisputeStatusUpdate
  where
    info :: TxInfo
    info = scriptContextTxInfo ctx
    
    validStateForDispute :: Bool
    validStateForDispute = apStatus datum `elem` [Pending, Confirmed]
    
    checkInvolvedParty :: Bool
    checkInvolvedParty = 
        txSignedBy info (apSender datum) || txSignedBy info (apRecipient datum)
    
    checkDisputeStatusUpdate :: Bool
    checkDisputeStatusUpdate = 
        case getContinuingOutputs ctx of
            [o] -> case txOutDatum o of
                OutputDatum (Datum d) -> 
                    case PlutusTx.fromBuiltinData d of
                        Just newDatum -> apStatus newDatum == Disputed
                        Nothing -> False
                _ -> False
            _ -> False

-- | Validate dispute resolution
{-# INLINABLE validateResolveDispute #-}
validateResolveDispute :: ArduinoPaymentDatum -> Bool -> ScriptContext -> Bool
validateResolveDispute datum resolution ctx =
    traceIfFalse "Payment not disputed" (apStatus datum == Disputed) &&
    traceIfFalse "Only arbitrator can resolve disputes" checkArbitratorSignature &&
    traceIfFalse "Must finalize payment status" checkResolutionStatusUpdate
  where
    info :: TxInfo
    info = scriptContextTxInfo ctx
    
    -- In a real implementation, this would check for a specific arbitrator key
    -- For now, we allow either party to resolve after a timeout
    checkArbitratorSignature :: Bool
    checkArbitratorSignature = 
        txSignedBy info (apSender datum) || txSignedBy info (apRecipient datum)
    
    checkResolutionStatusUpdate :: Bool
    checkResolutionStatusUpdate = 
        case getContinuingOutputs ctx of
            [o] -> case txOutDatum o of
                OutputDatum (Datum d) -> 
                    case PlutusTx.fromBuiltinData d of
                        Just newDatum -> 
                            if resolution 
                            then apStatus newDatum == Confirmed
                            else apStatus newDatum == Cancelled
                        Nothing -> False
                _ -> False
            _ -> False

-- | Helper function to get value paid to a specific address
{-# INLINABLE valuePaidTo #-}
valuePaidTo :: TxInfo -> PubKeyHash -> Value
valuePaidTo info pkh = 
    mconcat [txOutValue o | o <- txInfoOutputs info, 
             case txOutAddress o of
                 Address (PubKeyCredential pkh') _ -> pkh' == pkh
                 _ -> False]

-- | Typed validator
data ArduinoPayment
instance Scripts.ValidatorTypes ArduinoPayment where
    type instance DatumType ArduinoPayment = ArduinoPaymentDatum
    type instance RedeemerType ArduinoPayment = ArduinoPaymentRedeemer

typedValidator :: Scripts.TypedValidator ArduinoPayment
typedValidator = Scripts.mkTypedValidator @ArduinoPayment
    $$(PlutusTx.compile [|| arduinoPaymentValidator ||])
    $$(PlutusTx.compile [|| wrap ||])
  where
    wrap = Scripts.wrapValidator @ArduinoPaymentDatum @ArduinoPaymentRedeemer

-- | Validator script
validator :: Validator
validator = Scripts.validatorScript typedValidator

-- | Validator hash
validatorHash :: ValidatorHash
validatorHash = Scripts.validatorHash typedValidator

-- | Script address
scriptAddress :: Address
scriptAddress = scriptHashAddress validatorHash

-- | Helper functions for creating transactions

-- | Create a payment datum
mkPaymentDatum :: PubKeyHash -> PubKeyHash -> Integer -> BuiltinByteString -> 
                  BuiltinByteString -> BuiltinByteString -> Integer -> ArduinoPaymentDatum
mkPaymentDatum sender recipient amount paymentId productInfo arduinoSig timestamp =
    ArduinoPaymentDatum
        { apSender = sender
        , apRecipient = recipient
        , apAmount = amount
        , apPaymentId = paymentId
        , apProductInfo = productInfo
        , apArduinoSignature = arduinoSig
        , apStatus = Pending
        , apTimestamp = timestamp
        }

-- | Create execute payment redeemer
mkExecutePaymentRedeemer :: ArduinoPaymentRedeemer
mkExecutePaymentRedeemer = ExecutePayment

-- | Create confirm payment redeemer
mkConfirmPaymentRedeemer :: ArduinoPaymentRedeemer
mkConfirmPaymentRedeemer = ConfirmPayment

-- | Create cancel payment redeemer
mkCancelPaymentRedeemer :: ArduinoPaymentRedeemer
mkCancelPaymentRedeemer = CancelPayment

-- | Create dispute payment redeemer
mkDisputePaymentRedeemer :: BuiltinByteString -> ArduinoPaymentRedeemer
mkDisputePaymentRedeemer = DisputePayment

-- | Create resolve dispute redeemer
mkResolveDisputeRedeemer :: Bool -> ArduinoPaymentRedeemer
mkResolveDisputeRedeemer = ResolveDispute

-- | Script compilation
compiledScript :: CompiledCode (BuiltinData -> BuiltinData -> BuiltinData -> ())
compiledScript = $$(PlutusTx.compile [|| Scripts.wrapValidator @ArduinoPaymentDatum @ArduinoPaymentRedeemer arduinoPaymentValidator ||])

-- | Script serialization for deployment
scriptCBOR :: LBS.ByteString
scriptCBOR = serialise $ Scripts.validatorScript typedValidator

-- | Script hash for reference
scriptHash :: BuiltinByteString
scriptHash = 
    let hash = Scripts.validatorHash typedValidator
    in case hash of
        ValidatorHash bs -> bs