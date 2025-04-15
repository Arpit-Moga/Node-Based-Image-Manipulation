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
        position = ImVec2(100, 100);
    }

    void renderUI() override {
        ImGui::Text("%s", name.c_str());
        ImGui::InputText("Path", path, IM_ARRAYSIZE(path));
        if (ImGui::Button("Load")) {
            image = cv::imread(path);
        }
        if (!image.empty()) {
            ImGui::Text("Loaded: %dx%d", image.cols, image.rows);
        }
    }

    void process() override {}

    cv::Mat getOutput() override { return image; }

    void setInput(cv::Mat) override {}
};
