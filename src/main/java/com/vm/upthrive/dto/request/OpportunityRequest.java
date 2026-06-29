package com.vm.upthrive.dto.request;


import com.vm.upthrive.enums.OpportunityStatus;
import com.vm.upthrive.enums.OpportunityType;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.time.LocalDate;

@Data
public class OpportunityRequest {

    @NotBlank(message = "Title is required")
    private String title;

    @NotBlank(message ="Description is required")
    private String description;

    private Long companyId;

    private String location;

    private OpportunityType type;

    private String category;

    private String skillsRequired;

    private String applicationLink;

    private LocalDate deadline;

    private OpportunityStatus status;
}
