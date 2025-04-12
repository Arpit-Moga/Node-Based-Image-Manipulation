#pragma once
#include "NodeBase.h"

class ImageOutputNode : public Node {
private:
    cv::Mat inputImage;
    char outputPath[256] = "../Output.jpg";
    char inputKey[256] = "";

public:
    ImageOutputNode(int _id) {
        id = _id;
        name = "Image Output";
    }

    void renderUI() override {
        ImGui::Begin(("Node: " + name).c_str());
        ImGui::InputText("Input Key", inputKey, IM_ARRAYSIZE(inputKey));
        ImGui::InputText("Save Path", outputPath, IM_ARRAYSIZE(outputPath));
        if (ImGui::Button("Save") && !inputImage.empty()) {
            cv::imwrite(outputPath, inputImage);
        }
        ImGui::End();
    }

    void process() override {}

    cv::Mat getOutput() override { return inputImage; }

    void setInput(cv::Mat img) override { inputImage = img; }

    const char* getInputKey() { return inputKey; }
};