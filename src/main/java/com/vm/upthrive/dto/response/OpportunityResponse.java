package com.vm.upthrive.dto.response;


import com.vm.upthrive.enums.OpportunityStatus;
import com.vm.upthrive.enums.OpportunityType;
import lombok.Data;

import java.time.LocalDate;

@Data
public class OpportunityResponse {

    private Long id;

    private String title;

    private String description;

    private String companyName;

    private String location;

    private OpportunityType type;

    private String category;

    private String skillsRequired;

    private String applicationLink;

    private LocalDate deadline;

    private OpportunityStatus status;

}
