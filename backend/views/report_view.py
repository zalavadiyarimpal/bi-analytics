from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.services.query_builder import build_query
# from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated


import pandas as pd

class TabularReportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        from backend.validators.report_schema import validateReportConfig
        report_config = {
            "report_name": "Sales Summary",
            "data_source": {
                "type": "mysql",
                "connection_id": "sales_db",  
                "table": "salesorderheader"
            },
            "dimensions": {
                "rows": [
                    { "type": "column", "field": "DATE_FORMAT(orderdate, '%Y-%m')", "alias": "month" },
                    ],
                "measures": [
                    { "type": "agg", "agg": "sum", "field": "totaldue", "alias": "total_sales" }
                ]
            },
            "filters": {
                "orderdate": {
                    "operator": "between",
                    "value": ["2014-01-01", "2014-12-31"]
                }
            },
            "group_by": ["month"],
            "sort_by": [{
                "field": "month", 
                "order": "asc"}
            ],
            "limit": 10000
        }

        # validated_config = validateReportConfig(report_config)  # ✅ always a model
        # return Response({"data": validated_config.model_dump()})

        try:
            validated_config = validateReportConfig(report_config)
            validated_config = validated_config.model_dump()  # Convert to dict (Pydantic v2+)
            print(validated_config)
        except DRFValidationError as e:  # 🔁 Catch the DRF-level exception here
            return Response({
                "error": "ValidationErrorInConfig",
                "details": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            query, engine = build_query(validated_config)
            print("Generated SQL:\n", str(query))
            
            df = pd.read_sql(query, engine)
            return Response({
                    "success":True,
                    # "columns": list(df.columns),
                    "data": df.to_dict(orient='records')
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                    "error": "ValidationError",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        except sqlalchemy.exc.OperationalError as e:
            return Response({
                    "error": "SQLExecutionError",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                    "error": "UnknownError",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

