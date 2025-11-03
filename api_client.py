import requests
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChargeTemplate:
    def __init__(self, name: str, charge_name: str, charge_code: str, description: str, amount: str):
        self.name = name
        self.charge_name = charge_name
        self.charge_code = charge_code
        self.description = description
        self.amount = amount

class Profile:
    def __init__(self, _id: Optional[str] = None, name: str = "", profile_type: str = "", 
                 profile: Optional[Dict[str, Any]] = None, profile_group: List[Any] = None):
        self._id = _id
        self.name = name
        self.profile_type = profile_type
        self.profile = profile
        self.profile_group = profile_group or []

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "profileType": self.profile_type,
            "profile": self.profile,
            "profileGroup": self.profile_group
        }
        if self._id:
            data["_id"] = self._id
        return data

class ChargeProfileData:
    def __init__(self, template_id: str, name: str, description: str, amount: float, charge_id: str):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.amount = amount
        self.charge_id = charge_id

class CustomerRateRecord:
    def __init__(
        self,
        name: str,
        load_types: List[str],
        customers: List[Profile],
        pickup_location: List[Profile],
        delivery_location: List[Profile],
        terminals: List[Profile],
        effective_start_date: str,
        effective_end_date: str,
        charge_profile_data,
        description: str = "-",
        vendor_type: str = None,
        charge_profile_groups: List[str] = None 
    ):
        self.name = name
        self.load_types = load_types
        self.customers = customers
        self.pickup_location = pickup_location
        self.delivery_location = delivery_location
        self.terminals = terminals
        self.effective_start_date = effective_start_date
        self.effective_end_date = effective_end_date
        self.charge_profile_data = charge_profile_data
        self.description = description
        self.vendor_type = vendor_type
        self.charge_profile_groups = charge_profile_groups or []

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "loadType": self.load_types,
            "customers": [c.to_dict() for c in self.customers],
            "pickupLocation": [p.to_dict() for p in self.pickup_location],
            "deliveryLocation": [d.to_dict() for d in self.delivery_location],
            "returnLocation": None,
            "terminals": [t.to_dict() for t in self.terminals],
            "name": self.name,
            "effectiveStartDate": self.effective_start_date,
            "effectiveEndDate": self.effective_end_date,
            "containerType": None,
            "containerSize": None,
            "ssl": None,
            "csr": None,
            "customerDepartment": None,
            "chassisType": None,
            "chassisSize": None,
            "chassisOwner": None,
            "commodity": None,
            "hazmat": None,
            "overweight": None,
            "liquor": None,
            "hot": None,
            "genset": None,
            "domestic": None,
            "ev": None,
            "waste": None,
            "gdp": None,
            "isRail": None,
            "scale": None,
            "isStreetTurn": None,
            "chargeGroups": [{
                "billTo": {
                    "name": "Match Customer",
                    "profileType": "matchCustomer",
                    "profileGroup": [],
                    "profile": {"name": "Match Customer"}
                },
                "oneOffCharges": [],
                "chargeProfiles": [self.charge_profile_data],
                "chargeProfileGroups": [{"$oid": group_id} for group_id in self.charge_profile_groups]
            }],
            "description": self.description,
            "isActive": True,
        }

        if self.vendor_type is not None:
            data["vendorType"] = self.vendor_type

        return data

class PortProAPI:
    def __init__(self, base_url: str, token: str, vendor_type: str = None):
        """Initialize the PortPro API client.
        
        Args:
            base_url (str): The base URL for the API (e.g., 'https://sandbox-api.app.portpro.io')
            token (str): The authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.vendor_type = vendor_type
        
    def _get_headers(self) -> Dict[str, str]:
        """Get the common headers used in API requests."""
        return {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'authorization': f'Bearer {self.token}'
        }

    def create_charge_template(self, template: ChargeTemplate) -> Dict[str, Any]:
        """Create a new charge template.
        
        Args:
            template (ChargeTemplate): The charge template details
            
        Returns:
            Dict[str, Any]: The API response data field containing the created template
            
        Raises:
            ValueError: If the response doesn't contain the expected data structure
        """
        payload = {
            "autoAdd": True,
            "systemGenerated": False,
            "isActive": True,
            "isDeleted": False,
            "rules": [{
                "type": "GROUP",
                "value": "AND",
                "isNegated": False,
                "children": []
            }],
            "name": template.name,
            "chargeName": template.charge_name,
            "chargeCode": template.charge_code,
            "description": template.description,
            "fromEvent": None,
            "toEvent": None,
            "unitOfMeasure": "fixed",
            "charges": [{
                "minimumAmount": 0,
                "amount": template.amount,
                "freeUnits": 0
            }],
            "exactEvents": None,
            "inEvent": None
        }

        if self.vendor_type is not None:
            payload["vendorType"] = self.vendor_type
            payload["vendor"] = {
                "name": "All Driver Group",
                "profileType": "driverGroups/all",
                "profile": None,
                "profileGroup": [],
                "_id": "6811db7c60b4869eb9e26742"
            }
            payload["vendorId"] = None
            payload["vendorProfileType"] = "driverGroups/all"
        
        response = requests.post(
            f"{self.base_url}/charge-templates" if self.vendor_type != "driver" else f"{self.base_url}/rate-engine/vendor-rate/charge-profile",
            headers=self._get_headers(),
            json=payload
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        if 'data' not in response_json:
            raise ValueError("Unexpected response format: 'data' field missing")
            
        return response_json['data']

    def create_customer_rate_record(self, rate_record: CustomerRateRecord) -> Dict[str, Any]:
        """Create a new customer rate record.
        
        Args:
            rate_record (CustomerRateRecord): The customer rate record details
            
        Returns:
            Dict[str, Any]: The API response
        """
        
        response = requests.post(
            f"{self.base_url}/rate-engine/vendor-rate/load-tariff" if self.vendor_type == "driver" else f"{self.base_url}/customer-rate-record",
            headers=self._get_headers(),
            json=rate_record.to_dict()
        )
        
        response.raise_for_status()
        return response.json()