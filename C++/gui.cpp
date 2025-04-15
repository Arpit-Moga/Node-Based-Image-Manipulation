// gui.cpp
#include "ImageInputNode.h"
#include "BrightnessContrastNode.h"
#include "ImageOutputNode.h"
#include "BlurNode.h"

std::vector<Node*> nodes;
int current_id = 1;
std::vector<std::pair<int, int>> connections;
bool isLinking = false;
int linkingFromNode = -1;
ImVec2 linkingStart;

void renderGUI() {
    ImGui::Begin("Add Node");
    if (ImGui::Button("Add Input Node")) nodes.push_back(new ImageInputNode(current_id++));
    if (ImGui::Button("Add Brightness/Contrast Node")) nodes.push_back(new BrightnessContrastNode(current_id++));
    if (ImGui::Button("Add Output Node")) nodes.push_back(new ImageOutputNode(current_id++));
    ImGui::End();

    ImDrawList* draw_list = ImGui::GetBackgroundDrawList();
    ImVec2 mousePos = ImGui::GetIO().MousePos;

    for (auto& node : nodes) {
        ImVec2 nodePos = node->position;
        ImGui::SetNextWindowPos(nodePos, ImGuiCond_Always);
        ImGui::Begin(("##Node" + std::to_string(node->id)).c_str(), nullptr, ImGuiWindowFlags_NoTitleBar);

        node->renderUI();

        ImVec2 outputPos = ImGui::GetCursorScreenPos();
        outputPos.x += 120;
        outputPos.y += 20;
        ImGui::SetCursorScreenPos(outputPos);
        ImGui::InvisibleButton(("output" + std::to_string(node->id)).c_str(), ImVec2(10, 10));
        draw_list->AddCircleFilled(outputPos, 5, IM_COL32(255, 0, 0, 255));

        if (ImGui::IsItemHovered() && ImGui::IsMouseClicked(0)) {
            isLinking = true;
            linkingFromNode = node->id;
            linkingStart = outputPos;
        }

        ImVec2 inputPos = outputPos;
        inputPos.x -= 140;
        ImGui::SetCursorScreenPos(inputPos);
        ImGui::InvisibleButton(("input" + std::to_string(node->id)).c_str(), ImVec2(10, 10));

        bool canAcceptLink = isLinking && linkingFromNode != node->id;
        ImU32 color = canAcceptLink ? IM_COL32(0, 255, 255, 255) : IM_COL32(0, 255, 0, 255);
        draw_list->AddCircleFilled(inputPos, 5, color);

        if (ImGui::IsItemHovered() && ImGui::IsMouseReleased(0) && canAcceptLink) {
            connections.push_back({linkingFromNode, node->id});
            isLinking = false;
        }

        ImGui::End();
    }

    if (isLinking) {
        draw_list->AddBezierCubic(
            linkingStart,
            ImVec2(linkingStart.x + 50, linkingStart.y),
            ImVec2(mousePos.x - 50, mousePos.y),
            mousePos,
            IM_COL32(255, 255, 0, 255), 2.0f);

        if (ImGui::IsMouseReleased(0)) {
            isLinking = false;
        }
    }

    for (auto& conn : connections) {
        Node* outNode = nullptr;
        Node* inNode = nullptr;
        for (auto& n : nodes) {
            if (n->id == conn.first) outNode = n;
            if (n->id == conn.second) inNode = n;
        }
        if (outNode && inNode) {
            inNode->setInput(outNode->getOutput());
            inNode->process();

            ImVec2 p1 = outNode->position; p1.x += 120; p1.y += 20;
            ImVec2 p2 = inNode->position; p2.x -= 20;  p2.y += 20;
            draw_list->AddBezierCubic(p1, ImVec2(p1.x+50, p1.y), ImVec2(p2.x-50, p2.y), p2, IM_COL32(255,255,0,255), 2.0f);
        }
    }
}