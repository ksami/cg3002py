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

#define MAX_COUNT 32
#define WIDTH 64
#define HEIGHT 64
#define LEFT 60
#define RIGHT 68
#define THRESHOLD 15
char rawWindow[] = "Raw Video";
//char opticalFlowWindow[] = "Optical Flow Window";
char imageFileName[32];
long imageIndex = 0;
char keyPressed;


int main() {
	VideoCapture cap(0);
	cap.set(CV_CAP_PROP_FRAME_WIDTH, WIDTH);
	cap.set(CV_CAP_PROP_FRAME_HEIGHT, HEIGHT);

	Mat frame, grayFrames, rgbFrames, prevGrayFrame;
	Mat opticalFlow = Mat(cap.get(CV_CAP_PROP_FRAME_HEIGHT), cap.get(CV_CAP_PROP_FRAME_HEIGHT), CV_32FC3);
	cout << "prop frame width is: " << cap.get(CV_CAP_PROP_FRAME_WIDTH) << endl;
	cout << "prop frame height is: " << cap.get(CV_CAP_PROP_FRAME_HEIGHT) << endl;

	vector<Point2f> points1;
	vector<Point2f> points2;

	Point2f diff;

	int alt = 1;
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

	while (1) {
		cap >> rgbFrames;

		// fps
                time(&end);
                counter++;
                sec = difftime(end, start);
                fps = counter / sec;
                cout << "FPS: " << fps << endl;

		//frame.copyTo(rgbFrames);
		cvtColor(rgbFrames, grayFrames, CV_BGR2GRAY);

		if (needToInit) {
			goodFeaturesToTrack(grayFrames, points1, MAX_COUNT, 0.01, 5, Mat(), 3, 0, 0.04);
			needToInit = false;
		} else if (!points2.empty()) {
			//cout << "\n\n\nCalculating  calcOpticalFlowPyrLK\n\n\n\n\n";
			calcOpticalFlowPyrLK(prevGrayFrame, grayFrames, points2, points1, status, err, winSize, 3, termcrit, 0, 0.001);
			//cout << "status[0]: " << (int) status[0] << endl;
			//cout << "err[0]: " << err[0] << endl;
			//cout << "points2[0].x: " << points2[0].x << endl;
			//cout << "points1[0].x: " << points1[0].x << endl;

			//ignore weird pattern of triple same readings
			if (points2[0].x == points1[0].x)
				continue;

			// points2 is previous feature points, points1 is current
			for (i = 0; i < points2.size(); i++) {
				//cout << "Optical Flow Difference... X is " << int(points1[i].x - points2[i].x) << "\t Y is " << int(points1[i].y - points2[i].y) << "\t\t" << i	<< "\n";

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
				//circle(rgbFrames, points1[i], 2, Scalar(255, 0, 0), 1, 1, 0);

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
			circle(rgbFrames, foe, 6, Scalar(255, 255, 255), 1, 1, 0);
			circle(rgbFrames, Point(WIDTH/2, HEIGHT/2), 4, Scalar(255, 255, 255), 1, -1, 0);
			//cout << "foe: (" << foe.x << ", " << foe.y << ")" << endl;

			cout << "ttcArr { ";
			// calculate ttc for each point: distance from FoE / magnitude of optical flow vector
			for (i=0; i<points2.size(); i++) {
				dx = foe.x - points1[i].x;
				dy = foe.y - points1[i].y;
				mag = sqrt((dx*dx) + (dy*dy));
				ttcArr[i] = mag / magArr[i];
				
				// draw ttc with color
				if (ttcArr[i] > THRESHOLD){
					//red
					circle(rgbFrames, points1[i], 5, Scalar(0, 0, 255), 1, 1, 0);
				} else {
					//blue
					circle(rgbFrames, points1[i], 5, Scalar(255, 0, 0), 1, 1, 0);
				}

				cout << ttcArr[i] << ", ";
			}
			cout << "}" << endl;

			foex = 0.0;
			foey = 0.0;
			numFoe = 0.0;

			goodFeaturesToTrack(grayFrames, points1, MAX_COUNT, 0.01, 10, Mat(), 3, 0, 0.04);

		}
		imshow(rawWindow, rgbFrames);
		//imshow(opticalFlowWindow, opticalFlow);

		//std::swap(points2, points1);
		points2.clear();
		points2.swap(points1);
		//points1.clear();
		grayFrames.copyTo(prevGrayFrame);

		keyPressed = waitKey(10);
		if (keyPressed == 27) {
			break;
		}
		//else if (keyPressed == 'r') {
		//	opticalFlow = Mat(cap.get(CV_CAP_PROP_FRAME_HEIGHT), cap.get(CV_CAP_PROP_FRAME_HEIGHT), CV_32FC3);
		//}

	}
}

