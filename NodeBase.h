#pragma once
#include <opencv2/opencv.hpp>
#include <string>
#include <imgui.h>

class Node {
public:
    int id;
    std::string name;
    std::string outputKey;
    virtual void renderUI() = 0;
    virtual void process() = 0;
    virtual cv::Mat getOutput() = 0;
    virtual void setInput(cv::Mat img) = 0;
    virtual ~Node() {}
};