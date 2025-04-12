#include "ImageInputNode.h"
#include "BrightnessContrastNode.h"
#include "ImageOutputNode.h"
#include <vector>
#include <unordered_map>
#include <memory>

static int nodeIdCounter = 0;
static std::vector<std::shared_ptr<Node>> nodes;

void renderGUI() {
    ImGui::Begin("Add Node");
    if (ImGui::Button("Add Input Node")) {
        nodes.push_back(std::make_shared<ImageInputNode>(nodeIdCounter++));
    }
    if (ImGui::Button("Add Brightness/Contrast Node")) {
        nodes.push_back(std::make_shared<BrightnessContrastNode>(nodeIdCounter++));
    }
    if (ImGui::Button("Add Output Node")) {
        nodes.push_back(std::make_shared<ImageOutputNode>(nodeIdCounter++));
    }
    ImGui::End();

    std::unordered_map<std::string, cv::Mat> outputRegistry;

    for (auto& node : nodes) {
        node->renderUI();
    }

    for (auto& node : nodes) {
        if (auto* input = dynamic_cast<ImageInputNode*>(node.get())) {
            input->process();
            outputRegistry[input->outputKey] = input->getOutput();
        } else if (auto* bc = dynamic_cast<BrightnessContrastNode*>(node.get())) {
            auto it = outputRegistry.find(bc->getInputKey());
            if (it != outputRegistry.end()) {
                bc->setInput(it->second);
                bc->process();
                outputRegistry[bc->outputKey] = bc->getOutput();
            }
        } else if (auto* out = dynamic_cast<ImageOutputNode*>(node.get())) {
            auto it = outputRegistry.find(out->getInputKey());
            if (it != outputRegistry.end()) {
                out->setInput(it->second);
            }
        }
    }
}