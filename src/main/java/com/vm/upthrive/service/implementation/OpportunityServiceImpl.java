package com.vm.upthrive.service.implementation;

import com.vm.upthrive.dto.request.OpportunityRequest;
import com.vm.upthrive.dto.response.OpportunityResponse;
import com.vm.upthrive.repo.CompanyRepository;
import com.vm.upthrive.repo.OpportunityRepository;
import com.vm.upthrive.service.interfaces.OpportunityService;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class OpportunityServiceImpl implements OpportunityService {
    private final OpportunityRepository opportunityRepository;
    private final CompanyRepository companyRepository;

    public OpportunityServiceImpl(OpportunityRepository opportunityRepository,
                                  CompanyRepository companyRepository) {
        this.opportunityRepository = opportunityRepository;
        this.companyRepository = companyRepository;
    }

    @Override
    public OpportunityResponse createOpportunity(OpportunityRequest request) {
        return null;
    }

    @Override
    public List<OpportunityResponse> getAllOpportunity() {
        return List.of();
    }

    @Override
    public OpportunityResponse getopportunityById(Long id) {
        return null;
    }

    @Override
    public List<OpportunityResponse> getAllOpportunities() {
        return List.of();
    }

    @Override
    public OpportunityResponse getOpportunityById(Long id) {
        return null;
    }

    @Override
    public OpportunityResponse updateOpportunity(Long id, OpportunityRequest request) {
        return null;
    }

    @Override
    public void deleteOpportunity(Long id) {

    }

}
