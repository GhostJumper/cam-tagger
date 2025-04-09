package main

import (
	"fmt"
	"time"

	"github.com/tkrajina/gpxgo/gpx"
)

func main() {
	points, err := parseGPXFile("./samples/gpx/activity_18778134543.gpx")
	if err != nil {
		fmt.Println("\033[31mError parsing GPX file:", err)
		return
	}

	fmt.Println(points[0])

	/*
		point, err := findClosestGPXPoint(points, time.Date(2025, 4, 9, 14, 34, 0, 0, time.UTC), 1)
		if err != nil {
			fmt.Println("\033[31mError finding closest point:", err)
			return
		}

		fmt.Printf("Closest point: %v\n", point)
	*/

}

func parseGPXFile(gpxPath string) ([]gpx.GPXPoint, error) {

	gpxFile, err := gpx.ParseFile(gpxPath)
	if err != nil {
		return nil, err
	}

	//fmt.Println("GPX Info:", gpxFile.GetGpxInfo())

	points := make([]gpx.GPXPoint, 0)

	for _, track := range gpxFile.Tracks {
		for _, segment := range track.Segments {
			points = append(points, segment.Points...)
		}
	}

	if len(points) == 0 {
		return nil, fmt.Errorf("no points found in GPX file")
	}

	return points, nil
}

func offsetTimestamps(points []gpx.GPXPoint, offsetInMinutes int64) []gpx.GPXPoint {
	for i := range points {
		points[i].Timestamp = points[i].Timestamp.Add(time.Duration(offsetInMinutes) * time.Minute)
	}
	return points
}

func findClosestGPXPoint(points []gpx.GPXPoint, timestamp time.Time, maxDeviationTimeInMinutes int64) (gpx.GPXPoint, error) {
	var closestPoint = points[0]

	for _, point := range points {
		lastDeviation := closestPoint.Timestamp.Sub(timestamp).Abs()
		currentDeviation := point.Timestamp.Sub(timestamp).Abs()
		if currentDeviation < lastDeviation {
			closestPoint = point
		}
	}

	if closestPoint.Timestamp.Sub(timestamp).Minutes() > float64(maxDeviationTimeInMinutes) {
		return gpx.GPXPoint{}, fmt.Errorf("the closest point to %v is outside the allowed time deviation of %v minutes.\nThe closest point is %v at coordinates (%v, %v)",
			timestamp, maxDeviationTimeInMinutes, closestPoint.Timestamp.Sub(timestamp), closestPoint.Latitude, closestPoint.Longitude)
	}

	closestPoint.Comment = "Deviation: " + closestPoint.Timestamp.Sub(timestamp).String()
	return closestPoint, nil
}
