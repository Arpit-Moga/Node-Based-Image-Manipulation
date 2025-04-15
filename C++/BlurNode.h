#pragma once

#include "NodeBase.h"
#include "imgui.h"
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp> // Required for GaussianBlur

class BlurNode : public Node {
public:
    cv::Mat inputImage;
    cv::Mat outputImage;
    float blurRadius = 1.0f; // Default radius

    BlurNode(int id, const std::string& name, const ImVec2& position)
        : Node(id, name, position) {}

    void renderUI() override {
        ImGui::Begin(("Node: " + name + "##" + std::to_string(id)).c_str());
        ImGui::SetWindowPos(position, ImGuiCond_FirstUseEver); // Use position

        // Input slot
        ImGui::Text("Input");
        ImGui::SameLine(100); // Adjust alignment
        ImGui::Text("Output"); // Output slot (visual only for now)

        ImGui::Dummy(ImVec2(0.0f, 10.0f)); // Spacing

        // --- Node Specific UI ---
        ImGui::Text("Blur Radius:");
        // Ensure radius is odd and positive for GaussianBlur kernel size
        int kernelSize = static_cast<int>(blurRadius) * 2 + 1;
        if (ImGui::SliderFloat("##blur_radius", &blurRadius, 1.0f, 20.0f, "%.0f px")) {
             // Ensure kernel size is odd
            kernelSize = static_cast<int>(blurRadius) * 2 + 1;
            process(); // Re-process when slider changes
        }
        ImGui::Text("Kernel Size: %dx%d", kernelSize, kernelSize);


        ImGui::End();
    }

    void process() override {
        if (!inputImage.empty()) {
            // GaussianBlur requires kernel size to be odd and positive
            int ksize = static_cast<int>(blurRadius) * 2 + 1;
             if (ksize < 1) ksize = 1; // Ensure minimum kernel size of 1x1
            cv::GaussianBlur(inputImage, outputImage, cv::Size(ksize, ksize), 0);
        } else {
             // Handle case where there is no input image (optional: create empty mat)
             outputImage = cv::Mat();
        }
    }

    cv::Mat getOutput() override {
        return outputImage;
    }

    void setInput(const cv::Mat& input) override {
        inputImage = input.clone(); // Clone to avoid modifying the original
        process(); // Process immediately when input is set
    }
};