from django.shortcuts import render,redirect
import csv
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

class FileUpload(APIView):
    def get(self, request):
        return render(request, "index.html")

class CSVUploadView(APIView):
    def post(self, request):
        print("Request received")  # Debugging: Ensure the method is called
        if 'file' not in request.FILES:
            print("No file uploaded")  # Debugging: File is missing
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        print(f"File uploaded: {file.name}")  # Debugging: Log file name

        # Validate file extension
        if not file.name.endswith('.csv'):
            print("Invalid file type")  # Debugging: Wrong file type
            return Response({"error": "Only CSV files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = io.StringIO(file.read().decode('utf-8'))
            reader = csv.DictReader(decoded_file)
        except Exception as e:
            print(f"Error decoding file: {e}")  # Debugging: Log decoding error
            return Response({"error": f"Error reading CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        valid_records = []
        errors = []
        total_records = 0

        for index, row in enumerate(reader, start=1):
            total_records += 1
            serializer = UserSerializer(data=row)
            if serializer.is_valid():
                if not User.objects.filter(email=row['email']).exists():
                    valid_records.append(User(**serializer.validated_data))
            else:
                errors.append({"row_index": index, "row": row, "errors": serializer.errors})

        # Bulk insert valid records
        User.objects.bulk_create(valid_records)
        print(f"Uploaded {len(valid_records)} records successfully")  # Debugging: Log success

        return Response({
            "total_records": total_records,
            "saved_records": len(valid_records),
            "rejected_records": len(errors),
            "errors": errors
        }, status=status.HTTP_201_CREATED)
