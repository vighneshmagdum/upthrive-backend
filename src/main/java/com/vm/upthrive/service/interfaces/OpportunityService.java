package com.vm.upthrive.service.interfaces;

import com.vm.upthrive.dto.request.OpportunityRequest;
import com.vm.upthrive.dto.response.OpportunityResponse;

import java.util.List;

public interface OpportunityService {

    OpportunityResponse createOpportunity(OpportunityRequest request);

    List<OpportunityResponse> getAllOpportunity();

    OpportunityResponse getopportunityById(Long id);

    List<OpportunityResponse> getAllOpportunities();

    OpportunityResponse getOpportunityById(Long id);

    OpportunityResponse updateOpportunity(Long id, OpportunityRequest request);

    void deleteOpportunity(Long id);
}
