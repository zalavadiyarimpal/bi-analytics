from django.shortcuts import render
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sqlalchemy import create_engine, inspect
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from .cleaner import DynamicDataCleaner
from backend.db_connector import get_engine_create
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# from django.db import connection
# from rest_framework.permissions import AllowAny


class ImportDataSourceView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser]

    def post(self, request):
        # print(request,request.data)
        uploaded_file = request.FILES.get('dataset')
        table_name = request.data.get('table_name')
        datecolumn = request.data.get('datecolumn')
        is_create = request.data.get('is_create',False)
        datecolumns = False
        if datecolumn:
            datecolumns = [col.strip() for col in datecolumn.split(',') if col.strip()]
            
        # print(datecolumns)
        

        if not uploaded_file or not table_name:
            return Response({"error": "File and table_name are required"}, status=400)

        try:
            engine = get_engine_create()

            # engine = create_engine(
            #     f"mysql+pymysql://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
            # )

            # Clean and insert in chunks
            chunk_size = 10000
            first_chunk = is_create

            for chunk_df in pd.read_csv(uploaded_file, chunksize=chunk_size):
                # Clean the chunk

                cleaner = DynamicDataCleaner()
                cleaned_df = (cleaner.from_dataframe(chunk_df)
                                 .clean_column_names()
                                 .drop_duplicates()
                                 .trim_strings()
                                 .handle_missing()
                                 .convert_dates(datecolumns)
                                 .remove_outliers()
                                 .get_cleaned_data())
                # return Response({"message": f"Data saved to table '{table_name}' in chunks."}, status=201)
                # Insert into DB
                cleaned_df.to_sql(name=table_name, con=engine, if_exists='replace' if first_chunk else 'append', index=False)
                first_chunk = False

            return Response({"message": f"Data saved to table '{table_name}' in chunks."}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
