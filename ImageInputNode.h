#pragma once
#include "NodeBase.h"

class ImageInputNode : public Node {
private:
    cv::Mat image;
    char path[256] = "../Input.jpg";
public:
    ImageInputNode(int _id) {
        id = _id;
        name = "Image Input";
    }

    void renderUI() override {
        ImGui::Begin(("Node: " + name).c_str());
        ImGui::InputText("Path", path, IM_ARRAYSIZE(path));
        ImGui::InputText("Output Key", &outputKey[0], 256);
        if (ImGui::Button("Load")) {
            image = cv::imread(path);
        }
        if (!image.empty()) {
            ImGui::Text("Loaded: %dx%d", image.cols, image.rows);
        }
        ImGui::End();
    }

    void process() override {}

    cv::Mat getOutput() override { return image; }

    void setInput(cv::Mat) override {}
};