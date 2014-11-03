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

#define MAX_COUNT 500
#define WIDTH 128
#define HEIGHT 128
#define LEFT 60
#define RIGHT 68
char rawWindow[] = "Raw Video";
//char opticalFlowWindow[] = "Optical Flow Window";
char imageFileName[32];
long imageIndex = 0;
char keyPressed;


int main() {
	VideoCapture cap(0);
	cap.set(CV_CAP_PROP_FRAME_WIDTH, WIDTH);
	cap.set(CV_CAP_PROP_FRAME_HEIGHT, HEIGHT);

	Mat frame, grayFrames, rgbFrames, prevRgbFrame, prevGrayFrame;
	Mat opticalFlow = Mat(cap.get(CV_CAP_PROP_FRAME_HEIGHT), cap.get(CV_CAP_PROP_FRAME_HEIGHT), CV_32FC3);
	cout << "prop frame width is: " << cap.get(CV_CAP_PROP_FRAME_WIDTH) << endl;
	cout << "prop frame height is: " << cap.get(CV_CAP_PROP_FRAME_HEIGHT) << endl;

	vector<Point2f> points1;
	vector<Point2f> points2;

	Point2f diff;

	//int leftdx = 0;
	//int leftdy = 0;
	//int leftmag = 0;
	//int centdx = 0;
	//int centdy = 0;
	//int centmag = 0;
	//int rightdx = 0;
	//int rightdy = 0;
	//int rightmag = 0;
	Point2f pt;
	double dx, dy, mag;
	double a1, a2, b1, b2, c1, c2, det;
	double lineArr[MAX_COUNT][3];
	double magArr[MAX_COUNT];
	double foeArr[MAX_COUNT][2];
	double foex = 0.0;
	double foey = 0.0;
	int numFoe = 0;
	Point2f foe;
	double ttcArr[MAX_COUNT];
	Point leftBoundTop = Point(LEFT, 0);
	Point leftBoundBottom = Point(LEFT, HEIGHT);
	Point rightBoundTop = Point(RIGHT, 0);
	Point rightBoundBottom = Point(RIGHT, HEIGHT);

	time_t start, end;
	double fps, sec;
	int counter=0;

	vector<uchar> status;
	vector<float> err;

	RNG rng(12345);
	Scalar color = Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
	bool needToInit = true;

	int i, k;
	TermCriteria termcrit(CV_TERMCRIT_ITER | CV_TERMCRIT_EPS, 20, 0.03);
	Size subPixWinSize(10, 10), winSize(31, 31);
	namedWindow(rawWindow, CV_WINDOW_AUTOSIZE);
	double angle;

	time(&start);
	// gets a grid of 8x8
	for (i=16; i<HEIGHT; i+=32){
		for (k=16; k<WIDTH; k+=32){
			pt = Point(k, i);
			points2.push_back(pt);
		}
	}

	while (1) {
		cap >> frame;

		// fps
                time(&end);
                counter++;
                sec = difftime(end, start);
                fps = counter / sec;
                cout << "FPS: " << fps << endl;

		//frame.copyTo(rgbFrames);
		cvtColor(frame, rgbFrames, CV_BGR2GRAY);

		if (needToInit) {
			//goodFeaturesToTrack(grayFrames, points1, MAX_COUNT, 0.01, 5, Mat(), 3, 0, 0.04);
			needToInit = false;
		} else if (!points2.empty()) {
			//cout << "\n\n\nCalculating  calcOpticalFlowPyrLK\n\n\n\n\n";
			calcOpticalFlowPyrLK(prevRgbFrame, rgbFrames, points2, points1, status, err, winSize, 3, termcrit, 0, 0.001);
			cout << "points2[0].x: " << points2[0].x << endl;
			cout << "points1[0].x: " << points1[0].x << endl;
			// points2 is previous feature points, points1 is current
			for (i = 0; i < points2.size(); i++) {
				//cout << "Optical Flow Difference... X is " << int(points1[i].x - points2[i].x) << "\t Y is " << int(points1[i].y - points2[i].y) << "\t\t" << i	<< "\n";

				/*// Balance Strategy
				if (points1[i].x < LEFT) {
					//note: original is to get magnitude don't care abt direction
					leftdx += points1[i].x - points2[i].x;
					leftdy += points1[i].y - points2[i].y;
				} else if (points1[i].x > RIGHT) {
					rightdx += points1[i].x - points2[i].x;
					rightdy += points1[i].y - points2[i].y;
					line(rgbFrames, points1[i], points2[i], Scalar(0, 255, 0), 1, 1, 0);
				} else {
					centdx += points1[i].x - points2[i].x;
					centdy += points1[i].y - points2[i].y;
					line(rgbFrames, points1[i], points2[i], Scalar(255, 255, 0), 1, 1, 0);
				}*/


				//draw the optical flow vector
				line(rgbFrames, points1[i], points2[i], Scalar(0, 255, 0), 1, 1, 0);

				// Eqn of lines Ax+By=C
				a1 = points2[i].y - points1[i].y;
				b1 = points1[i].x - points2[i].x;
				c1 = (a1 * points1[i].x) + (b1 * points1[i].x);
				lineArr[i][0] = a1;
				lineArr[i][1] = b1;
				lineArr[i][2] = c1;

				// Find length of vector, vector points from old points2 to new points1
				dx = points1[i].x - points2[i].x;
				dy = points1[i].y - points2[i].y;
				mag = sqrt((dx * dx) + (dy * dy));
				magArr[i] = mag;

				// Draw feature points
				circle(rgbFrames, points1[i], 2, Scalar(255, 0, 0), 1, 1, 0);

				//points1[k++] = points1[i];

			}

			// find intersections of lines
			for (i=0; i<points2.size(); i+=2) {
				a1 = lineArr[i][0];
				b1 = lineArr[i][1];
				c1 = lineArr[i][2];
				a2 = lineArr[i+1][0];
				b2 = lineArr[i+1][1];
				c2 = lineArr[i+1][2];
				det = (a1*b2)-(a2*b1);
				//cout << "det[i]: " << det << endl;
				if(det <= 0.0) {
					//parallel lines
				} else {
					foeArr[numFoe][0] = ((b2*c1) - (b1*c2)) / det;
					foeArr[numFoe][1] = ((a1*c2) - (a2*c1)) / det;
					//cout << "foeArr[k]: (" << foeArr[k][0] << ", " << foeArr[k][1]  << ")" << endl;
					numFoe++;
				}
			}

			// average out to get FoE
			for (i=0; i<numFoe; i++) {
				foex = foex + foeArr[i][0];
				foey = foey + foeArr[i][1];
			}
			//cout << "foe.x: " << foe.x << ", foex: " << foex << endl;
			//cout << "foe.y: " << foe.y << ", foey: " << foey << endl;
			//cout << "numFoe: " << numFoe << endl;
			foe.x = foex / numFoe;
			foe.y = foey / numFoe;
			//draw foe
			circle(rgbFrames, foe, 10, Scalar(255, 255, 255), 1, 1, 0);
			circle(rgbFrames, Point(64,64), 5, Scalar(255, 255, 255), 1, -1, 0);
			//cout << "foe: (" << foe.x << ", " << foe.y << ")" << endl;

			//cout << "ttcArr { ";
			// calculate ttc for each point: distance from FoE / magnitude of optical flow vector
			for (i=0; i<points2.size(); i++) {
				dx = foe.x - points1[i].x;
				dy = foe.y - points1[i].y;
				mag = sqrt((dx*dx) + (dy*dy));
				ttcArr[i] = mag / magArr[i];
			//	cout << ttcArr[i] << ", ";
			}
			//cout << "}" << endl;

			foex = 0.0;
			foey = 0.0;
			numFoe = 0.0;

			//goodFeaturesToTrack(grayFrames, points1, MAX_COUNT, 0.01, 10, Mat(), 3, 0, 0.04);

		}
		// Show the boundaries
		//line(rgbFrames, leftBoundTop, leftBoundBottom, Scalar(255, 255, 255), 1, 1, 0);
		//line(rgbFrames, rightBoundTop, rightBoundBottom, Scalar(255, 255, 255), 1, 1, 0);

		//leftmag = sqrt((leftdx*leftdx) + (leftdy*leftdy));		
		//rightmag = sqrt((rightdx*rightdx) + (rightdy*rightdy));		
		//centmag = sqrt((centdx*centdx) + (centdy*centdy));		
		
		//if (leftmag > rightmag) {
		//	cout << "move towards left" << endl;
		//} else if (leftmag < rightmag) {
		//	cout << "move towards rightright" << endl;
		//} else {
		//	cout << "go straight" << endl;
		//}

		//cout << "leftmag: " << leftmag << " centmag: " << centmag << " rightmag: " << rightmag << endl;
		//cout << "leftdx: " << leftdx << " leftdy: " << leftdy << endl;
		//cout << "rightdx: " << rightdx << " rightdy: " << rightdy << endl;
		//cout << "centdx: " << centdx << " centdy: " << centdy << endl;

		//leftmag = leftdx = leftdy = 0;
		//rightmag = rightdx = rightdy = 0;
		//centmag = centdx = centdy = 0;
		

		//imshow(rawWindow, grayFrames);
		imshow(rawWindow, rgbFrames);
		//imshow(opticalFlowWindow, opticalFlow);

		//std::swap(points2, points1);
		//points1.clear();
		rgbFrames.copyTo(prevRgbFrame);

		keyPressed = waitKey(10);
		if (keyPressed == 27) {
			break;
		}
		//else if (keyPressed == 'r') {
		//	opticalFlow = Mat(cap.get(CV_CAP_PROP_FRAME_HEIGHT), cap.get(CV_CAP_PROP_FRAME_HEIGHT), CV_32FC3);
		//}

	}
}

