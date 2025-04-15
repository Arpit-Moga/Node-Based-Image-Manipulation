// #pragma once
#include "NodeBase.h"

class BrightnessContrastNode : public Node {
private:
    float brightness = 0.0f;
    float contrast = 1.0f;
    cv::Mat inputImage, outputImage;

public:
    BrightnessContrastNode(int _id) {
        id = _id;
        name = "Brightness & Contrast";
        position = ImVec2(300, 100);
    }

    void renderUI() override {
        ImGui::Text("%s", name.c_str());
        ImGui::SliderFloat("Brightness", &brightness, -100.0f, 100.0f);
        ImGui::SliderFloat("Contrast", &contrast, 0.0f, 3.0f);
    }

    void process() override {
        if (!inputImage.empty()) {
            inputImage.convertTo(outputImage, -1, contrast, brightness);
        }
    }

    cv::Mat getOutput() override { return outputImage; }

    void setInput(cv::Mat img) override { inputImage = img; }
};