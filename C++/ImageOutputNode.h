#pragma once
#include "NodeBase.h"

class ImageOutputNode : public Node {
private:
    cv::Mat inputImage;
    char outputPath[256] = "../Output.jpg";
public:
    ImageOutputNode(int _id) {
        id = _id;
        name = "Image Output";
        position = ImVec2(500, 100);
    }

    void renderUI() override {
        ImGui::Text("%s", name.c_str());
        ImGui::InputText("Save Path", outputPath, IM_ARRAYSIZE(outputPath));
        if (ImGui::Button("Save") && !inputImage.empty()) {
            cv::imwrite(outputPath, inputImage);
        }
    }

    void process() override {}

    cv::Mat getOutput() override { return inputImage; }

    void setInput(cv::Mat img) override { inputImage = img; }
};