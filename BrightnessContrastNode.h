#pragma once
#include "NodeBase.h"

class BrightnessContrastNode : public Node {
private:
    float brightness = 0.0f;
    float contrast = 1.0f;
    cv::Mat inputImage, outputImage;
    char inputKey[256] = "";

public:
    BrightnessContrastNode(int _id) {
        id = _id;
        name = "Brightness & Contrast";
    }

    void renderUI() override {
        ImGui::Begin(("Node: " + name).c_str());
        ImGui::InputText("Input Key", inputKey, IM_ARRAYSIZE(inputKey));
        ImGui::InputText("Output Key", &outputKey[0], 256);
        ImGui::SliderFloat("Brightness", &brightness, -100.0f, 100.0f);
        ImGui::SliderFloat("Contrast", &contrast, 0.0f, 3.0f);
        ImGui::End();
    }

    void process() override {
        if (!inputImage.empty()) {
            inputImage.convertTo(outputImage, -1, contrast, brightness);
        }
    }

    cv::Mat getOutput() override { return outputImage; }

    void setInput(cv::Mat img) override { inputImage = img; }

    const char* getInputKey() { return inputKey; }
};