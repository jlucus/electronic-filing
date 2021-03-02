FORM_803 = {
    "name": "FPPC 803",
    "title": "",
    "reference_urls": [
        (
            "https://www.fppc.ca.gov/learn/public-officials-and-employees-rules-/behested-payment-report.html",
            "Instructions at FPPC Website",
        )
    ],
    "schema": {
        "parts": [
            {
                "part_number": 1,
                "title": "Identification",
                "fields": [
                    {"id": 0, "label": "Last Name", "type": "{last_name}"},
                    {"id": 1, "label": "First Name", "type": "{first_name}"},
                    {"id": 2, "label": "Agency Name", "type": "{agency_name_803}"},
                    {"id": 3, "label": "Official Type", "type": "{official_type_803}"},
                    {
                        "id": 4,
                        "label": "Agency Street Address",
                        "type": "{steet_address}",
                    },
                    {
                        "id": 5,
                        "label": "Designated Contact Person",
                        "type": "{person_name}",
                    },
                    {
                        "id": 6,
                        "label": "Designated Contact Email Address",
                        "type": "{email_address}",
                    },
                    {
                        "id": 7,
                        "label": "Area Code/Phone Number",
                        "type": "{phone_number}",
                    },
                    {"id": 8, "label": "Amendement", "type": "{optional:bool}"},
                    {
                        "id": 9,
                        "label": "Date of Original Filing",
                        "type": "{contingent:date}",
                    },
                ],
            },
            {
                "part_number": 2,
                "title": "Payor Information",
                "fields": [
                    {"id": 0, "label": "Name", "type": "{person_name}"},
                    {"id": 1, "label": "International Address", "type": "{bool}"},
                    {"id": 2, "label": "Street Address", "type": "{street_address}"},
                    {"id": 3, "label": "City", "type": "{city_name}"},
                    {"id": 4, "label": "State", "type": "{state_name}"},
                    {"id": 5, "label": "Zip Code", "type": "{zip_code}"},
                ],
            },
            {
                "part_number": 3,
                "title": "Payee Information",
                "fields": [
                    {"id": 0, "label": "Name", "type": "{person_name}"},
                    {"id": 1, "label": "International Address", "type": "{bool}"},
                    {"id": 2, "label": "Street Address", "type": "{street_address}"},
                    {"id": 3, "label": "City", "type": "{city_name}"},
                    {"id": 4, "label": "State", "type": "{state_name}"},
                    {"id": 5, "label": "Zip Code", "type": "{zip_code}"},
                ],
            },
            {
                "part_number": 4,
                "title": "Payment Information",
                "fields": [
                    {"id": 0, "label": "Date of Payment", "type": "{date_mmddyy}"},
                    {"id": 1, "label": "Amount", "type": "{usd_int}"},
                    {
                        "id": 2,
                        "label": "Payment Type",
                        "type": "select_one",
                        "options": {0: "Monetary", 1: "In-King Goods or Services",},
                    },
                    {
                        "id": 3,
                        "label": "Brief Description of In-Kind Payment",
                        "type": "{contingent}",
                        "dependent_fields": [{"part": 4, "field_id": 2, "option": 1,}],
                    },
                    {
                        "id": 4,
                        "label": "Purpose",
                        "type": "{select_one}",
                        "options": {
                            0: "Legislative",
                            1: "Governmental",
                            2: "Charitable",
                        },
                    },
                    {
                        "id": 5,
                        "label": "Describe the legislative, governmental, charitable purpose, or event",
                        "type": "{description}",
                    },
                ],
            },
            {
                "part_number": 5,
                "title": "Amendement Description or Comments",
                "fields": [],
            },
            {
                "part_number": 6,
                "title": "Verification",
                "fields": [
                    {"id": 0, "label": "Executed on", "type": "{execution_date}"},
                    {
                        "id": 1,
                        "label": "Executed by",
                        "type": "{signature}",
                        "note": "",
                    },
                ],
            },
        ],
    },
}
