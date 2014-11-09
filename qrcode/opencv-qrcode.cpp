#include <opencv2/highgui/highgui.hpp>
#include <opencv2/video/tracking.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include <iostream>
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <time.h>

using namespace cv;
using namespace std;

#define WIDTH 320
#define HEIGHT 240
//char rawWindow[] = "Raw Video";
//char keyPressed;


#include "zbar.h"  
using namespace zbar;  


int main(void){  
	VideoCapture cap(0);
	cap.set(CV_CAP_PROP_FRAME_WIDTH, WIDTH);
	cap.set(CV_CAP_PROP_FRAME_HEIGHT, HEIGHT);

	ImageScanner scanner;  
	scanner.set_config(ZBAR_NONE, ZBAR_CFG_ENABLE, 1);  
	// obtain image data  
	//char file[256];  
	//cin>>file;  
	//Mat img = imread(file,0);  
	Mat img;
	Mat gray;

	time_t start, end;
	double fps, sec;
	int counter=0;

	time(&start);  

	while(1){
		cap >> img;
		cvtColor(img,gray,CV_BGR2GRAY);  
		int width = img.cols;  
		int height = img.rows;  
		uchar *raw = (uchar *)gray.data;  

		// fps
		time(&end);
		counter++;
		sec = difftime(end, start);
		fps = counter / sec;
		cout << "FPS: " << fps << endl;

		//cout<<"image captured"<<endl;

		// wrap image data  
		Image image(width, height, "Y800", raw, width * height);  

		//cout<<"scanning"<<endl;

		// scan the image for barcodes  
		int n = scanner.scan(image);  

		cout<<"n: "<<n<<endl;

		if(n>0){

			// extract results  
			for(Image::SymbolIterator symbol = image.symbol_begin(); symbol != image.symbol_end(); ++symbol) {  
				vector<Point> vp;  
				// do something useful with results  
				cout << "decoded " << symbol->get_type_name()  
					<< " symbol \"" << symbol->get_data() << '"' <<" "<< endl;  
				int n = symbol->get_location_size();  
				for(int i=0;i<n;i++){  
					vp.push_back(Point(symbol->get_location_x(i),symbol->get_location_y(i))); 
				}  
				RotatedRect r = minAreaRect(vp);  
				Point2f pts[4];  
				r.points(pts);  
				//for(int i=0;i<4;i++){  
				//     line(imgout,pts[i],pts[(i+1)%4],Scalar(255,0,0),3);  
				//}  
				cout<<"Angle: "<<r.angle<<endl;  
			}  
			//imshow("imgout.jpg",imgout);  
			// clean up  
			image.set_data(NULL, 0);  
			//waitKey();
		}  
	}  
}



/*
   int main() {
   VideoCapture cap(0);
   cap.set(CV_CAP_PROP_FRAME_WIDTH, WIDTH);
   cap.set(CV_CAP_PROP_FRAME_HEIGHT, HEIGHT);

   Mat frame, rgbFrames;
   cout << "prop frame width is: " << cap.get(CV_CAP_PROP_FRAME_WIDTH) << endl;
   cout << "prop frame height is: " << cap.get(CV_CAP_PROP_FRAME_HEIGHT) << endl;

   time_t start, end;
   double fps, sec;
   int counter = 0;

   Size subPixWinSize(10, 10), winSize(31, 31);
//namedWindow(rawWindow, CV_WINDOW_AUTOSIZE);

time(&start);

while (1) {
cap >> frame;

// fps
time(&end);
counter++;
sec = difftime(end, start);
fps = counter / sec;
cout << "FPS: " << fps << endl;

frame.copyTo(rgbFrames);

//imshow(rawWindow, rgbFrames);

keyPressed = waitKey(10);
if (keyPressed == 27) {
break;
}

}
}
 */


