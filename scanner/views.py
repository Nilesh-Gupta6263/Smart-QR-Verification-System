from django.shortcuts import render

from .models import QRCode
import qrcode
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path
import cv2
from PIL import Image
# from pyzbar.pyzbar import decode

def generate_qr(request):
    qr_image_url=None
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        data = request.POST.get('qr_data')

        # validate the mobile number
        if not mobile_number or len(mobile_number) != 10 or not mobile_number.isdigit():
            return render(request, 'scanner/generate.html',{'error':'invalid mobile number'})
        #generate the qr code image with the data and mobile number
        qr_content=f"{data}|{mobile_number}"
        qr = qrcode.make(qr_content)
        qr_image_io = BytesIO() # create a BytesIO stream

        #save the qr image or qr_image_io
        qr.save(qr_image_io, format='PNG')
        # reset the position of the stream
        qr_image_io.seek(0)

        #define the storage location for the qr code images 
        #use of file system storage ContentFile
        qr_storage_path = settings.MEDIA_ROOT / 'qr_codes'
        fs = FileSystemStorage(location=qr_storage_path,base_url='/media/qr_codes/')
        filename = f"{data}_{mobile_number}.PNG"
        qr_image_content=ContentFile(qr_image_io.read(),name=filename)
        file_path = fs.save(filename, qr_image_content)
        qr_image_url = fs.url(filename)

         #save the qr code data and mobile number in the database
        QRCode.objects.create(data=data,mobile_number=mobile_number)

        # print("POST DATA:", request.POST)
        # print("DATA VALUE:", data)

    return render(request, 'scanner/generate.html',{'qr_image_url':qr_image_url})





# def scan_qr(request):
#     result = None

#     if request.method == 'POST' and request.FILES.get('qr_image'):
#         mobile_number = request.POST.get('mobile_number')
#         qr_image = request.FILES['qr_image']

#         # Validate mobile number
#         if not mobile_number or len(mobile_number) != 10 or not mobile_number.isdigit():
#             return render(request, 'scanner/scan.html', {
#                 'error': 'Invalid mobile number'
#             })

#         # Save uploaded image
#         fs = FileSystemStorage()
#         filename = fs.save(qr_image.name, qr_image)
#         image_path = Path(fs.location) / filename

#         try:
#             # Open image and decode QR
#             image = Image.open(image_path)
#             decoded_objects = decode(image)

#             if decoded_objects:
#                 qr_content = decoded_objects[0].data.decode('utf-8').strip()

#         
#                 qr_data, qr_mobile_number = qr_content.split('|')

#                     # Check database
#                     qr_entry = QRCode.objects.filter(
#                         data=qr_data,
#                         mobile_number=qr_mobile_number
#                     ).first()

#                     if qr_entry and qr_mobile_number == mobile_number:
#                         result = "Scan Success: Valid QR Code"
#                         qr_entry.delete()

#                         # Delete stored QR code image
#                         qr_image_path = Path(settings.MEDIA_ROOT) / 'qr_codes' / \
#                             f"{qr_data}_{qr_mobile_number}.png"

#                         if qr_image_path.exists():
#                             qr_image_path.unlink()

#                     else:
#                         result = "Scan Failed: Invalid QR or mobile mismatch"
#             else:
#                 result = "No QR code detected in the image"

#         except Exception as e:
#             result = f"Error processing the image: {str(e)}"

#         finally:
#             # Delete uploaded image after processing
#             if image_path.exists():
#                 image_path.unlink()

#     return render(request, 'scanner/scan.html', {'result': result})


def scan_qr(request):
    result = None
    if request.method == 'POST' and request.FILES.get('qr_image'):
        mobile_number = request.POST.get('mobile_number')
        qr_image = request.FILES['qr_image']
          # validate the mobile number
        if not mobile_number or len(mobile_number) != 10 or not mobile_number .isdigit():
            return render(request, 'scanner/scan.html',{'error':'invalid mobile number'})
        
        #save the upload image
        fs = FileSystemStorage()
        filename=fs.save(qr_image.name, qr_image)
        image_path = Path(fs.location) / filename
        try:
            #open the image and decode it
            img =cv2.imread(str(image_path))
            detector = cv2.QRCodeDetector()
            # Open image and decode QR
            qr_content ,bbox, _ = detector.detectAndDecode(img)
            if qr_content:

#               
# #             

#                 decoded_objects= decode(image)
#             if decoded_objects:
#                 #get the data from the first decoded objects
#                 qr_content = decoded_objects[0].data.decode('utf-8').strip()

                if '|' not in qr_content:
                    result = "Invalid QR format"
                else:
                    qr_data, qr_mobile_number = qr_content.split('|')

                # check if the data exist in the QRCode model with the provided mibile number
                qr_entry = QRCode.objects.filter(data=qr_data,mobile_number=qr_mobile_number).first()


                if qr_entry and qr_mobile_number == mobile_number:
                    result = "Scan Success: Valid QR Code for the provided mobile number"
                    qr_entry.delete()  #  delete the qrcode image from the media/qr_codes directory

                    
                    qr_image_path = Path(settings.MEDIA_ROOT)/'qr_codes'/ \
                        f"{qr_data}_{qr_mobile_number}.png"
                    

                    if qr_image_path.exists():
                        qr_image_path.unlink() #delete the qr code image
                    #delete the uploaded image from the media folder
                       
                else:
                    result="SCAN FAILED: invalid qr code or mobile number mismatch"
            else:
                result = "NO QR CODE DETECTED IN THE IMAGE"        


            
        except Exception as e:
            result = f"Error processing the image:{str(e)}"
        finally:
            if image_path.exists():
                image_path.unlink() 
                        
    return render(request, 'scanner/scan.html',{'result':result})

